import neovim
import subprocess
import json
import time

from itertools import *

@neovim.plugin
class NeoRtags(object):
    def __init__(self, vim):
        self.vim = vim

    def init_mapping(self):
        self.vim.command('let g:mapleader=","')
        self.register_mapping('ri', 'NeoRtagsSymbolInfo')
        self.register_mapping('rc', 'NeoRtagsFindSubclasses')
        self.register_mapping('rC', 'NeoRtagsFindSuperclasses')
        self.register_mapping('rd', 'NeoRtagsDiagnose')
        self.register_mapping('rj', 'NeoRtagsFollowLocation')
        self.register_mapping('rl', 'NeoRtagsListProjects')
        self.register_mapping('rf', 'NeoRtagsFindReferences')
        self.register_mapping('rn', 'NeoRtagsFindReferencesByName')
        self.register_mapping('rp', 'NeoRtagsJumpToParent')
        self.register_mapping('rv', 'NeoRtagsFindVirtuals')
        self.register_mapping('rw', 'NeoRtagsRenameSymbol')

        # register code completion if there's any
        if self.vim.command('echo &completeopt') == None:
            self.vim.command('set completeopt=menuone,noinsert')
            self.vim.command('set completefunc=NeoRtagsCompleteFunction')

    def register_mapping(self, keys, function):
        self.vim.command('noremap <Leader>%s :call %s()<CR>' % (keys, function))

    @neovim.autocmd('VimEnter', sync = True)
    def on_vim_enter(self):
        self.init_mapping()

    @neovim.function('NeoRtagsSymbolInfo', sync = True)
    def symbol_info(self, args):
        rc, stdout, stderr = self.run_command ('--absolute-path -U %s' % self.get_current_location())

        if rc == 0:
            # skip first line as it prints filename and content of current line
            self.vim.api.out_write(stdout[stdout.find('\n'):])
        else:
            self.vim.api.err_write(stdout)

    @neovim.function('NeoRtagsFindReferences')
    def find_references(self, args):
        cmd = '--absolute-path -r %s -e --json' % self.get_current_location()
        self.show_quickfix_locations (cmd)

    @neovim.function('NeoRtagsFindReferencesByName')
    def find_references_by_name(self, args):
        output = self.vim.funcs.input('Symbol: ')
        cmd = '--absolute-path -a -R %s -e --json' % output
        self.show_quickfix_locations (cmd)

    @neovim.function('NeoRtagsFollowLocation')
    def follow_location(self, args):
        # TODO: jump in buffer where the request was triggered
        rc, stdout, stderr = self.run_command ('--absolute-path -f %s' % self.get_current_location())
        if rc == 0 and len(stdout) > 0:
            self.jump_to_location(stdout)

    @neovim.function('NeoRtagsJumpToParent')
    def jump_to_parent(self, args):
        # TODO: jump in buffer where the request was triggered
        rc, stdout, stderr = self.run_command ('--absolute-path -U %s --symbol-info-include-parents --json' % self.get_current_location())
        if rc == 0:
            result = json.loads(stdout)
            if 'parent' in result:
                self.jump_to_location(result['parent']['location'])

    @neovim.function('NeoRtagsFindSubclasses')
    def find_subclasses(self, args):
        self.show_classes(True)

    @neovim.function('NeoRtagsFindSuperclasses')
    def find_superclasses(self, args):
        self.show_classes(False)

    @neovim.function('NeoRtagsListProjects', sync = True)
    def find_list_projects(self, args):
        rc, stdout, stderr = self.run_command ('-w')
        if rc == 0:
            projects = stdout.strip().split('\n')
            s = ''
            for i, p in enumerate(projects):
                s += '%d: %s\n' % (i + 1, p)
            self.vim.api.out_write(s)
            number = self.vim.funcs.input('Project number: ')
            try:
                id = int(number)
                if id > 0 and id <= len(projects):
                    rc, stdout, stderr = self.run_command ('-w %d' % id)
                # TODO: check return value
            except ValueError:
                pass

    @neovim.function('NeoRtagsFindVirtuals', sync = True)
    def find_virtuals(self, args):
        cmd = '--absolute-path -r %s -k --json' % self.get_current_location()
        self.show_quickfix_locations (cmd)

    @neovim.function('NeoRtagsDiagnose')
    def diagnose(self, args):
        # delete signs
        self.vim.command('sign unplace *')

        # save current buffer
        self.vim.command(':w')

        # TODO: fix by using of a blocking version of the --diagnose command
        time.sleep(1.5);

        buffer = self.vim.current.buffer
        cmd = '--diagnose %s --synchronous-diagnostics --json' % buffer.name
        rc, stdout, stderr = self.run_command (cmd)

        if rc == 0:
            files = json.loads(stdout)['checkStyle']
            keys = list(files.keys())
            assert len(keys) == 1
            filename, errors = list(files.items())[0]
            if errors == None:
                return

            assert filename == buffer.name

            quickfix_errors = []

            # set up sign style
            self.vim.command('sign define fixit text=F texthl=FixIt')
            self.vim.command('sign define warning text=W texthl=Warning')
            self.vim.command('sign define error text=E texthl=Error')

            for i, e in enumerate(errors):
                if e['type'] == 'skipped':
                    continue

                # strip error prefix
                s = ' Issue: '
                index = e['message'].find(s)
                if index != -1:
                    e['message'] = e['message'][index + len(s):]
                    error_type = 'E' if e['type'] == 'error' else 'W'
                    quickfix_errors.append({'lnum': e['line'], 'col': e['column'],
                        'nr': i, 'text': e['message'], 'filename': filename,
                        'type': error_type})
                    cmd = 'sign place %d line=%s name=%s file=%s' % (i + 1, e['line'], e['type'], filename)
                    self.vim.command(cmd)

            # show errors in quickfix window
            if len(quickfix_errors) > 0:
                self.vim.funcs.setqflist(quickfix_errors)
                self.vim.command(':copen')
            else:
                self.vim.command(':cclose')

    @neovim.function('NeoRtagsRenameSymbol', sync = True)
    def rename_symbol(self, args):
        new_name = self.vim.funcs.input('New name: ')
        cmd = '--absolute-path -r %s -e --rename --json' % self.get_current_location()
        rc, stdout, stderr = self.run_command (cmd)
        if rc == 0:
            data = json.loads(stdout)
            locations = list(reversed([(x['loc'].split(':')[0], x['loc']) for x in data]))

            # self.vim.api.err_write(str(locations))

            self.vim.command(':w')
            if len(locations) > 0:
                rename_all = False
                for filename, g in groupby(locations, key = lambda x: x[0]):
                    if not rename_all:
                        r = self.vim.funcs.confirm('Rename in %s' % filename, "&Yes\nYes to &All\n&No\n&Cancel")
                        if r == 1:
                            pass
                        elif r == 2:
                            rename_all = True
                        elif r == 3:
                            continue
                        elif r == 4:
                            self.vim.command(':w')
                            return

                    for l in g:
                        self.jump_to_location(l[1])
                        self.vim.command('normal! ciw%s' % new_name)
                    self.vim.command(':w')

    @neovim.function('NeoRtagsCompleteFunction', sync = True)
    def complete_code(self, args):
        findstart = int(args[0])
        base = args[1]

        buffer = self.vim.current.buffer
        cursor = self.vim.current.window.cursor
        linenum = cursor[0] - 1
        column = cursor[1] - 1

        if findstart:
            line = buffer[linenum]
            while column > 0 and line[column].isalnum() or line[column] == '_':
                column -= 1

            return column + 1
        else:
            content = '\n'.join(buffer[:])
            cmd = ('--synchronous-completions -l %s:%d:%d --unsaved-file=%s:%d --json'
                % (buffer.name, linenum + 1, column + len(base) + 2, buffer.name, len(content)))
            if len(base) > 0:
                cmd += ' --code-complete-prefix %s' % base

            rc, stdout, stderr = self.run_command (cmd, content)
            if rc == 0:
                result = json.loads(stdout)
                completions = self.parse_completion_results(result)
                return {'words': completions, 'refresh': 'always'}

    def get_current_location(self):
        cursor = self.vim.current.window.cursor
        buffer = self.vim.current.buffer
        return '%s:%d:%d' % (buffer.name, cursor[0], cursor[1] + 1)

    def run_command(self, arguments, content = None):
        r = subprocess.run('rc ' + arguments,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                input = content,
                encoding = 'utf8',
                shell = True)

        return (r.returncode, r.stdout, r.stderr)

    def parse_completion_results(self, result):
        completions = []

        for c in result['completions']:
            k = c['kind']
            kind = ''
            if k == 'FunctionDecl' or k == 'FunctionTemplate':
                kind = 'f'
            elif k == 'CXXMethod' or k == 'CXXConstructor':
                kind = 'm'
            elif k == 'VarDecl' or k == 'FieldDecl':
                kind = 'v'
            elif k == 'macro definition':
                kind = 'd'
            elif k == 'EnumDecl':
                kind = 'e'
            elif k == 'TypedefDecl' or k == 'StructDecl' or k == 'EnumConstantDecl':
                kind = 't'

            match = {'menu': c['completion'], 'word': c['completion'], 'kind': kind}
            completions.append(match)

        return completions

    def parse_quickfix_locations(self, data):
        locations = []

        for d in data:
            parts = d['loc'].split(':')
            assert len(parts) == 4
            locations.append({
                'filename': parts[0],
                'lnum': int(parts[1]),
                'col': int(parts[2]),
                'text': d['ctx']
                })

        return locations

    def show_classes(self, subclasses):
        classes = self.get_classes(subclasses)
        if classes != None and len(classes) > 0:
            self.vim.funcs.setqflist(self.classes_to_quickfix_locations(classes))
            self.vim.command(':copen')

    def show_quickfix_locations(self, cmd):
        rc, stdout, stderr = self.run_command (cmd)
        if rc == 0:
            data = json.loads(stdout)
            locations = self.parse_quickfix_locations(data)

            if len(locations) > 0:
                self.vim.funcs.setqflist(locations)
                self.vim.command(':copen')

    def classes_to_quickfix_locations(self, lines):
        locations = []

        for l in lines:
            parts = l.split('\t')
            assert len(parts) == 3
            location = parts[1].split(':')

            locations.append({
                'filename': location[0],
                'lnum': int(location[1]),
                'col': int(location[2]),
                'text': parts[2]
                })

        return locations

    def get_classes(self, subclasses):
        # TODO: rewrite the API in rtags to provide JSON result
        rc, stdout, stderr = self.run_command ('--absolute-path --class-hierarchy %s' % self.get_current_location())

        if rc != 0 or stdout == '':
            return None
        else:
            lines = [x.strip() for x in stdout.strip().split('\n')]
            sub_classes = []
            super_classes = []
            in_super = False
            for l in lines:
                if l == 'Superclasses:':
                    in_super = True
                elif l == 'Subclasses:':
                    in_super = False
                else:
                    if in_super:
                        super_classes.append(l)
                    else:
                        sub_classes.append(l)

            return sub_classes if subclasses else super_classes

    def jump_to_location(self, location):
        parts = location.split(':')
        filename = parts[0]
        if filename != self.vim.current.buffer.name:
            self.vim.command(':e ' + filename)
        self.vim.current.window.cursor = [int(parts[1]), int(parts[2]) - 1]

