#! /usr/bin/env python
# based on https://github.com/FWGS/xash3d-fwgs/blob/master/wscript

from waflib import Build, Configure, Context, Logs
import os.path

VERSION = '0.01'
APPNAME = 'OpenCSGO'
top = '.'
default_prefix = os.path.abspath('../game')

Context.Context.line_just = 60 # should fit for everything on 80x26

PROJECTS = [
	'appframework',
	'd3dx',
	'generated_proto',
	'interfaces',
	'mathlib',
	'thirdparty/cryptopp-8.9.0',
	'thirdparty/dxvk-native-1.9.2b/src/d3d9',
	'thirdparty/dxvk-native-1.9.2b/src/dxso',
	'thirdparty/dxvk-native-1.9.2b/src/dxvk',
	'thirdparty/dxvk-native-1.9.2b/src/spirv',
	'thirdparty/dxvk-native-1.9.2b/src/util',
	'thirdparty/dxvk-native-1.9.2b/src/vulkan',
	'thirdparty/dxvk-native-1.9.2b/src/wsi',
	'thirdparty/freetype-2.13.2',
	'thirdparty/goldberg_emulator/dll',
	'thirdparty/protobuf-3.6.1/src',
	'tier0',
	'tier1',
	'tier2',
	'tier3',
	'vstdlib'
]

@Configure.conf
def get_taskgen_count(self):
	try: idx = self.tg_idx_count
	except: idx = 0 # don't set tg_idx_count to not increase counter
	return idx

def options(opt):
	opt.load('reconfigure compiler_optimizations compiler_c compiler_cxx ndk clang_compilation_database strip_on_install msdev msvs msvc subproject ccache')

	grp = opt.add_option_group('Common options')

	grp.add_option('-8', '--64bits', action = 'store_true', dest = 'ALLOW64', default = False,
		help = 'allow targetting 64-bit engine [default: %default]')

	grp.add_option('-w', '--no-warnings', action = 'store_true', dest = 'NO_WARNINGS', default = False,
		help = 'disable warnings [default: %default]')

	grp.add_option('-d', '--dedicated', action = 'store_true', dest = 'DEDICATED', default = False,
		help = 'build dedicated server [default: %default]')

	opt.add_subproject(PROJECTS)

def configure(conf):
	conf.load('fwgslib reconfigure ndk compiler_optimizations')
	conf.env.MSVC_TARGETS = ['x86' if not conf.options.ALLOW64 else 'x64']

	# Force XP compatibility, all build targets should add subsystem=bld.env.MSVC_SUBSYSTEM
	if conf.env.MSVC_TARGETS[0] == 'x86':
		conf.env.MSVC_SUBSYSTEM = 'WINDOWS,5.01'
	else:
		conf.env.MSVC_SUBSYSTEM = 'WINDOWS'

	conf.env.ALLOW64	=		conf.options.ALLOW64
	conf.env.DEDICATED	=		conf.options.DEDICATED

	if conf.env.DEST_OS == 'android':
		conf.env.BINPATH = conf.env.GAMEBIN = conf.env.PREFIX + '/lib'
	else:
		conf.env.BINPATH = conf.env.PREFIX + '/bin'
		conf.env.GAMEBIN = conf.env.PREFIX + '/csgo/bin'

	# Load compilers early
	conf.load('compiler_c compiler_cxx ndk ccache')

	# HACKHACK: override msvc DEST_CPU value by something that we understand
	if conf.env.DEST_CPU == 'amd64':
		conf.env.DEST_CPU = 'x86_64'

	if conf.env.COMPILER_CC == 'msvc':
		conf.load('msvc_pdb')

	conf.load('msvs msdev subproject clang_compilation_database strip_on_install enforce_pic')

	enforce_pic = True # modern defaults
	conf.check_pic(enforce_pic)

	cflags, linkflags = conf.get_optimization_flags()
	cxxflags = list(cflags) # optimization flags are common between C and C++ but we need a copy

	if conf.env.COMPILER_CC in ['gcc', 'clang']:
		conf.env.append_unique('CFLAGS_cshlib', ['-fPIC'])
		conf.env.append_unique('CXXFLAGS_cxxshlib', ['-fPIC'])

	conf.check_cc(cflags=cflags, linkflags=linkflags, msg='Checking for required C flags')
	conf.check_cxx(cxxflags=cxxflags, linkflags=linkflags, msg='Checking for required C++ flags')

	conf.env.append_unique('CFLAGS', cflags)
	conf.env.append_unique('CXXFLAGS', cxxflags)
	conf.env.append_unique('LINKFLAGS', linkflags)

	opt_flags = []
	opt_cflags = []
	opt_cxxflags = []

	if conf.options.NO_WARNINGS and conf.env.COMPILER_CC in ['gcc', 'clang']:
		opt_flags += ['-w']

	if conf.env.COMPILER_CC == 'clang':
		opt_flags += ['-fcolor-diagnostics']
	elif conf.env.COMPILER_CC == 'gcc':
		opt_flags += ['-fdiagnostics-color=always']

	if conf.env.COMPILER_CC in ['gcc', 'clang']:
		opt_flags += ['-m64']
	elif conf.env.COMPILER_CC == 'msvc':
		opt_flags += ['/MACHINE:X64']

	if conf.env.COMPILER_CC == 'msvc':
		opt_cxxflags += ['/std:c++17']
	elif conf.env.COMPILER_CC in ['gcc', 'clang']:
		opt_cxxflags += ['-std=c++17']

	cflags = conf.filter_cflags(opt_flags + opt_cflags, cflags)
	cxxflags = conf.filter_cxxflags(opt_flags + opt_cxxflags, cxxflags)

	conf.env.append_unique('CFLAGS', cflags)
	conf.env.append_unique('CXXFLAGS', cxxflags)

#	if conf.env.DEST_OS == 'win32':
#		a = []
#		if conf.env.COMPILER_CC == 'msvc':
#			for i in a:
#				conf.start_msg('Checking for MSVC library')
#				conf.check_lib_msvc(i)
#				conf.end_msg(i)
#		else:
#			for i in a:
#				conf.check_cc(lib = i)

	includes = [
		os.path.abspath('public'),
		os.path.abspath('public/tier0'),
		os.path.abspath('public/tier1'),
		os.path.abspath('common'),
		os.path.abspath('thirdparty/protobuf-3.6.1/src'),
		os.path.abspath('thirdparty/DirectXMath-dec2023/Inc')
	]

	if conf.env.COMPILER_CC == 'msvc':
		conf.define('COMPILER_MSVC', True)
		conf.define('_CRT_SECURE_NO_WARNINGS', True)
		if conf.env.ALLOW64:
			conf.define('COMPILER_MSVC64', True)
		else:
			conf.define('COMPILER_MSVC32', True)
	elif conf.env.COMPILER_CC in ['gcc', 'clang']:
		conf.define('COMPILER_GCC', True)

	if conf.env.DEST_OS == 'win32': # TODO: IMPLETE ME!
		conf.define('_WIN32', True)
		conf.define('WIN32', True)
		conf.define('_DLL_EXT', '.dll', quote=False)
	else:
		conf.define('_POSIX', True)
		conf.define('POSIX', True)
		conf.define('USE_SDL', True)
		if conf.env.DEST_OS in ['linux', 'android']:
			conf.define('_LINUX', True)
			conf.define('LINUX', True)
			conf.define('GNUC', True)
			conf.define('_DLL_EXT', '.so', quote=False)
		if conf.env.DEST_OS == 'android':
			conf.define('ANDROID', True)
			conf.check_cc(lib='android', uselib_store='android')
			conf.check_cc(lib='log', uselib_store='android_log')
			conf.check_cc(lib='OpenSLES', uselib_store='OpenSLES')
			includes += [os.path.abspath('thirdparty/SDL-2.28.5/include')]
		else:
			conf.check_cfg(package='sdl2', args='--cflags --libs', uselib_store='SDL2')
			includes += conf.env.INCLUDES_SDL2
		includes += [os.path.abspath('thirdparty/freetype-2.13.2/include')]

	conf.define('PLATFORM_64BITS', True)
	conf.define('CSTRIKE15', True)
	conf.define('CSTRIKE_REL_BUILD', True)
	conf.define('VPROF_LEVEL', True)
	conf.define('RAD_TELEMETRY_DISABLED', True)

	if conf.env.DEST_OS != 'win32':
		conf.define('DX_TO_VK_ABSTRACTION', True)
		includes += [
			os.path.abspath('thirdparty/dxvk-native-1.9.2b/include/native/windows'),
			os.path.abspath('thirdparty/dxvk-native-1.9.2b/include/native/directx')
		]
	else:
		conf.define('USE_ACTUAL_DX', True)

	if conf.options.BUILD_TYPE == 'debug':
		conf.define('DEBUG',1)
		conf.define('_DEBUG',1)
	else:
		conf.define('NDEBUG',1)

	if conf.env.DEDICATED:
		conf.define('DEDICATED', True)

	conf.env.append_unique('INCLUDES', includes)

	conf.add_subproject(PROJECTS)

def build(bld):
	bld.add_subproject(PROJECTS)
