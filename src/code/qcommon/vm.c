/*
===========================================================================
Copyright (C) 1999-2005 Id Software, Inc.

This file is part of Quake III Arena source code.

Quake III Arena source code is free software; you can redistribute it
and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the License,
or (at your option) any later version.

Quake III Arena source code is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
===========================================================================
*/
// vm.c -- virtual machine

/*


intermix code and data
symbol table

a dll has one imported function: VM_SystemCall
and one exported function: Perform


*/

#include "vm_local.h"
#include "../ui/ui_public.h"
#include "../cgame/cg_public.h"
#include "../cgame/tr_types.h"
#include "../game/g_public.h"
#include <stdint.h>

#ifndef UI_OLD_API_VERSION
#define UI_OLD_API_VERSION 4
#endif


vm_t	*currentVM = NULL; // bk001212
vm_t	*lastVM    = NULL; // bk001212
int		vm_debugLevel;
static cvar_t	*vm_trace;

static fileHandle_t vmTraceHandle;
static qboolean vmTraceOpenAttempted;

#define	MAX_VM		3
vm_t	vmTable[MAX_VM];


void VM_VmInfo_f( void );
void VM_VmProfile_f( void );


// converts a VM pointer to a C pointer and
// checks to make sure that the range is acceptable
void	*VM_VM2C( vmptr_t p, int length ) {
	return (void *)p;
}

void VM_Debug( int level ) {
	vm_debugLevel = level;
}

/*
=============
VM_OpenTraceLog

Opens the trace log lazily when tracing is enabled.
=============
*/
static fileHandle_t VM_OpenTraceLog( void ) {
	fileHandle_t handle;

	if ( vmTraceHandle ) {
		return vmTraceHandle;
	}

	if ( vmTraceOpenAttempted ) {
		return 0;
	}

	vmTraceOpenAttempted = qtrue;
	handle = FS_FOpenFileAppend( "vm_trace.log" );
	if ( handle <= 0 ) {
		vmTraceOpenAttempted = qfalse;
		return 0;
	}

	vmTraceHandle = handle;
	return vmTraceHandle;
}

/*
=============
VM_CloseTraceLog

Closes the active trace log handle when tracing completes.
=============
*/
static void VM_CloseTraceLog( void ) {
	if ( vmTraceHandle ) {
		FS_FCloseFile( vmTraceHandle );
		vmTraceHandle = 0;
	}

	vmTraceOpenAttempted = qfalse;
}

/*
=============
VM_LogTraceEvent

Writes a formatted line to the trace log when vm_trace is enabled.
=============
*/
static void VM_LogTraceEvent( const char *fmt, ... ) {
	fileHandle_t handle;
	char buffer[1024];
	va_list args;
	int length;

	if ( !vm_trace || !vm_trace->integer ) {
		return;
	}

	handle = VM_OpenTraceLog();
	if ( !handle ) {
		return;
	}

	va_start( args, fmt );
	length = Q_vsnprintf( buffer, sizeof( buffer ), fmt, args );
	va_end( args );

	if ( length < 0 ) {
		VM_CloseTraceLog();
		return;
	}

	if ( length >= sizeof( buffer ) ) {
		length = sizeof( buffer ) - 1;
	}
	buffer[length++] = '\n';

	FS_Write( buffer, length, handle );
	VM_CloseTraceLog();
}

/*
==============
VM_Init
==============
*/
void VM_Init( void ) {
	Cvar_Get( "vm_cgame", "0", CVAR_ARCHIVE );	// Quake Live ships native modules by default.
	Cvar_Get( "vm_game", "0", CVAR_ARCHIVE );	// Quake Live ships native modules by default.
	Cvar_Get( "vm_ui", "0", CVAR_ARCHIVE );		// Quake Live ships native modules by default.
	vm_trace = Cvar_Get( "vm_trace", "0", CVAR_TEMP );
	vmTraceHandle = 0;
	vmTraceOpenAttempted = qfalse;

	Cmd_AddCommand ("vmprofile", VM_VmProfile_f );
	Cmd_AddCommand ("vminfo", VM_VmInfo_f );

	Com_Memset( vmTable, 0, sizeof( vmTable ) );
}


/*
===============
VM_ValueToSymbol

Assumes a program counter value
===============
*/
const char *VM_ValueToSymbol( vm_t *vm, int value ) {
	vmSymbol_t	*sym;
	static char		text[MAX_TOKEN_CHARS];

	sym = vm->symbols;
	if ( !sym ) {
		return "NO SYMBOLS";
	}

	// find the symbol
	while ( sym->next && sym->next->symValue <= value ) {
		sym = sym->next;
	}

	if ( value == sym->symValue ) {
		return sym->symName;
	}

	Com_sprintf( text, sizeof( text ), "%s+%i", sym->symName, value - sym->symValue );

	return text;
}

/*
===============
VM_ValueToFunctionSymbol

For profiling, find the symbol behind this value
===============
*/
vmSymbol_t *VM_ValueToFunctionSymbol( vm_t *vm, int value ) {
	vmSymbol_t	*sym;
	static vmSymbol_t	nullSym;

	sym = vm->symbols;
	if ( !sym ) {
		return &nullSym;
	}

	while ( sym->next && sym->next->symValue <= value ) {
		sym = sym->next;
	}

	return sym;
}


/*
===============
VM_SymbolToValue
===============
*/
int VM_SymbolToValue( vm_t *vm, const char *symbol ) {
	vmSymbol_t	*sym;

	for ( sym = vm->symbols ; sym ; sym = sym->next ) {
		if ( !strcmp( symbol, sym->symName ) ) {
			return sym->symValue;
		}
	}
	return 0;
}


/*
=====================
VM_SymbolForCompiledPointer
=====================
*/
const char *VM_SymbolForCompiledPointer( vm_t *vm, void *code ) {
	int			i;

	if ( code < (void *)vm->codeBase ) {
		return "Before code block";
	}
	if ( code >= (void *)(vm->codeBase + vm->codeLength) ) {
		return "After code block";
	}

	// find which original instruction it is after
	for ( i = 0 ; i < vm->codeLength ; i++ ) {
		if ( (void *)vm->instructionPointers[i] > code ) {
			break;
		}
	}
	i--;

	// now look up the bytecode instruction pointer
	return VM_ValueToSymbol( vm, i );
}



/*
===============
ParseHex
===============
*/
int	ParseHex( const char *text ) {
	int		value;
	int		c;

	value = 0;
	while ( ( c = *text++ ) != 0 ) {
		if ( c >= '0' && c <= '9' ) {
			value = value * 16 + c - '0';
			continue;
		}
		if ( c >= 'a' && c <= 'f' ) {
			value = value * 16 + 10 + c - 'a';
			continue;
		}
		if ( c >= 'A' && c <= 'F' ) {
			value = value * 16 + 10 + c - 'A';
			continue;
		}
	}

	return value;
}

/*
===============
VM_LoadSymbols
===============
*/
void VM_LoadSymbols( vm_t *vm ) {
	int		len;
	char	*mapfile, *text_p, *token;
	char	name[MAX_QPATH];
	char	symbols[MAX_QPATH];
	vmSymbol_t	**prev, *sym;
	int		count;
	int		value;
	int		chars;
	int		segment;
	int		numInstructions;

	// don't load symbols if not developer
	if ( !com_developer->integer ) {
		return;
	}

	COM_StripExtension( vm->name, name );
	Com_sprintf( symbols, sizeof( symbols ), "vm/%s.map", name );
	len = FS_ReadFile( symbols, (void **)&mapfile );
	if ( !mapfile ) {
		Com_Printf( "Couldn't load symbol file: %s\n", symbols );
		return;
	}

	numInstructions = vm->instructionPointersLength >> 2;

	// parse the symbols
	text_p = mapfile;
	prev = &vm->symbols;
	count = 0;

	while ( 1 ) {
		token = COM_Parse( &text_p );
		if ( !token[0] ) {
			break;
		}
		segment = ParseHex( token );
		if ( segment ) {
			COM_Parse( &text_p );
			COM_Parse( &text_p );
			continue;		// only load code segment values
		}

		token = COM_Parse( &text_p );
		if ( !token[0] ) {
			Com_Printf( "WARNING: incomplete line at end of file\n" );
			break;
		}
		value = ParseHex( token );

		token = COM_Parse( &text_p );
		if ( !token[0] ) {
			Com_Printf( "WARNING: incomplete line at end of file\n" );
			break;
		}
		chars = strlen( token );
		sym = Hunk_Alloc( sizeof( *sym ) + chars, h_high );
		*prev = sym;
		prev = &sym->next;
		sym->next = NULL;

		// convert value from an instruction number to a code offset
		if ( value >= 0 && value < numInstructions ) {
			value = vm->instructionPointers[value];
		}

		sym->symValue = value;
		Q_strncpyz( sym->symName, token, chars + 1 );

		count++;
	}

	vm->numSymbols = count;
	Com_Printf( "%i symbols parsed from %s\n", count, symbols );
	FS_FreeFile( mapfile );
}

/*
============
VM_DllSyscall

Dlls will call this directly

 rcg010206 The horror; the horror.

  The syscall mechanism relies on stack manipulation to get it's args.
   This is likely due to C's inability to pass "..." parameters to
   a function in one clean chunk. On PowerPC Linux, these parameters
   are not necessarily passed on the stack, so while (&arg[0] == arg)
   is true, (&arg[1] == 2nd function parameter) is not necessarily
   accurate, as arg's value might have been stored to the stack or
   other piece of scratch memory to give it a valid address, but the
   next parameter might still be sitting in a register.

  Quake's syscall system also assumes that the stack grows downward,
   and that any needed types can be squeezed, safely, into a signed int.

  This hack below copies all needed values for an argument to a
   array in memory, so that Quake can get the correct values. This can
   also be used on systems where the stack grows upwards, as the
   presumably standard and safe stdargs.h macros are used.

  As for having enough space in a signed int for your datatypes, well,
   it might be better to wait for DOOM 3 before you start porting.  :)

  The original code, while probably still inherently dangerous, seems
   to work well enough for the platforms it already works on. Rather
   than add the performance hit for those platforms, the original code
   is still in use there.

  For speed, we just grab 15 arguments, and don't worry about exactly
   how many the syscall actually needs; the extra is thrown away.
 
============
*/
int QDECL VM_DllSyscall( int arg, ... ) {
  const char *module = currentVM ? currentVM->name : "unknown";
#if ((defined __linux__) && (defined __powerpc__))
  // rcg010206 - see commentary above
  int args[SYSCALL_CONTRACT_MAX_ARGS];
  int i;
  va_list ap;

  args[0] = arg;

  va_start(ap, arg);
  for (i = 1; i < SYSCALL_CONTRACT_MAX_ARGS; i++) {
    args[i] = va_arg(ap, int);
  }
  va_end(ap);

  SyscallContract_LogEvent( "vm-dll", module, args, SYSCALL_CONTRACT_MAX_ARGS );
  return currentVM->systemCall( args );
#else // original id code
  int captured[SYSCALL_CONTRACT_MAX_ARGS];
  int index;
  const int *stack = &arg;

  for ( index = 0 ; index < SYSCALL_CONTRACT_MAX_ARGS ; index++ ) {
    captured[index] = stack[index];
  }
  SyscallContract_LogEvent( "vm-dll", module, captured, SYSCALL_CONTRACT_MAX_ARGS );
  return currentVM->systemCall( &arg );
#endif
}

/*
=================
VM_Restart

Reload the data, but leave everything else in place
This allows a server to do a map_restart without changing memory allocation
=================
*/
vm_t *VM_Restart( vm_t *vm ) {
	vmHeader_t	*header;
	int			length;
	int			dataLength;
	int			i;
	char		filename[MAX_QPATH];

	// DLL's can't be restarted in place
	if ( vm->dllHandle ) {
		char	name[MAX_QPATH];
	    int			(*systemCall)( int *parms );
		void		*dllImports;
		int			dllApiVersion;
		
		systemCall = vm->systemCall;
		dllImports = vm->dllImports;
		dllApiVersion = vm->dllApiVersion;
		Q_strncpyz( name, vm->name, sizeof( name ) );

		VM_Free( vm );

		vm = VM_Create( name, systemCall, VMI_NATIVE, dllImports, dllApiVersion );
		return vm;
	}

	// load the image
	Com_Printf( "VM_Restart()\n", filename );
	Com_sprintf( filename, sizeof(filename), "vm/%s.qvm", vm->name );
	Com_Printf( "Loading vm file %s.\n", filename );
	length = FS_ReadFile( filename, (void **)&header );
	if ( !header ) {
		Com_Error( ERR_DROP, "VM_Restart failed.\n" );
	}

	// byte swap the header
	for ( i = 0 ; i < sizeof( *header ) / 4 ; i++ ) {
		((int *)header)[i] = LittleLong( ((int *)header)[i] );
	}

	// validate
	if ( header->vmMagic != VM_MAGIC
		|| header->bssLength < 0 
		|| header->dataLength < 0 
		|| header->litLength < 0 
		|| header->codeLength <= 0 ) {
		VM_Free( vm );
		Com_Error( ERR_FATAL, "%s has bad header", filename );
	}

	// round up to next power of 2 so all data operations can
	// be mask protected
	dataLength = header->dataLength + header->litLength + header->bssLength;
	for ( i = 0 ; dataLength > ( 1 << i ) ; i++ ) {
	}
	dataLength = 1 << i;

	// clear the data
	Com_Memset( vm->dataBase, 0, dataLength );

	// copy the intialized data
	Com_Memcpy( vm->dataBase, (byte *)header + header->dataOffset, header->dataLength + header->litLength );

	// byte swap the longs
	for ( i = 0 ; i < header->dataLength ; i += 4 ) {
		*(int *)(vm->dataBase + i) = LittleLong( *(int *)(vm->dataBase + i ) );
	}

	// free the original file
	FS_FreeFile( header );

	return vm;
}

/*
================
VM_Create

If image ends in .qvm it will be interpreted, otherwise
it will attempt to load as a system dll
================
*/

#define	STACK_SIZE	0x20000

vm_t *VM_Create( const char *module, int (*systemCalls)(int *),
		vmInterpret_t interpret, void *dllImports, int dllApiVersion ) {
	vm_t		*vm;
	vmHeader_t	*header;
	int			length;
	int			dataLength;
	int			i, remaining;
	char		filename[MAX_QPATH];

	if ( !module || !module[0] || !systemCalls ) {
		Com_Error( ERR_FATAL, "VM_Create: bad parms" );
	}

	remaining = Hunk_MemoryRemaining();

	// see if we already have the VM
	for ( i = 0 ; i < MAX_VM ; i++ ) {
		if (!Q_stricmp(vmTable[i].name, module)) {
			vm = &vmTable[i];
			return vm;
		}
	}

	// find a free vm
	for ( i = 0 ; i < MAX_VM ; i++ ) {
		if ( !vmTable[i].name[0] ) {
			break;
		}
	}

	if ( i == MAX_VM ) {
		Com_Error( ERR_FATAL, "VM_Create: no free vm_t" );
	}

	vm = &vmTable[i];

	Q_strncpyz( vm->name, module, sizeof( vm->name ) );
	vm->systemCall = systemCalls;
	vm->dllExports = NULL;
	vm->dllImports = dllImports;
	vm->dllApiVersion = dllApiVersion;
	vm->dllInterface = qfalse;

	// never allow dll loading with a demo
	if ( interpret == VMI_NATIVE ) {
		if ( Cvar_VariableValue( "fs_restrict" ) ) {
			interpret = VMI_COMPILED;
		}
	}

	if ( interpret == VMI_NATIVE ) {
		// try to load as a system dll
		Com_Printf( "Loading dll file %s.\n", vm->name );
		vm->dllHandle = Sys_LoadDll( module, vm->fqpath, &vm->entryPoint,
			&vm->dllExports, vm->dllImports,
			vm->dllImports ? &vm->dllApiVersion : NULL, VM_DllSyscall );
		if ( vm->dllHandle ) {
			if ( !Q_stricmp( module, "ui" ) && vm->entryPoint && !vm->dllExports && vm->dllImports ) {
				int uiApi;

				uiApi = vm->entryPoint( UI_GETAPIVERSION );
				Com_Printf( "UI native vmMain API reported %d\n", uiApi );
				if ( uiApi == UI_API_VERSION || uiApi == UI_OLD_API_VERSION || uiApi == dllApiVersion ) {
					vm->dllApiVersion = uiApi;
				}
			}

			if ( vm->dllExports ) {
				vm->dllInterface = qtrue;
			}
			VM_LogTraceEvent( "create %s native %s", module, vm->fqpath );
			return vm;
		}

		Com_Printf( "Failed to load dll, looking for qvm.\n" );
		interpret = VMI_COMPILED;
	}

	// load the image
	Com_sprintf( filename, sizeof(filename), "vm/%s.qvm", vm->name );
	Com_Printf( "Loading vm file %s.\n", filename );
	length = FS_ReadFile( filename, (void **)&header );
	if ( !header ) {
		Com_Printf( "Failed.\n" );
		VM_LogTraceEvent( "create %s failed qvm", module );
		VM_Free( vm );
		return NULL;
	}

	// byte swap the header
	for ( i = 0 ; i < sizeof( *header ) / 4 ; i++ ) {
		((int *)header)[i] = LittleLong( ((int *)header)[i] );
	}

	// validate
	if ( header->vmMagic != VM_MAGIC
		|| header->bssLength < 0 
		|| header->dataLength < 0 
		|| header->litLength < 0 
		|| header->codeLength <= 0 ) {
		VM_Free( vm );
		Com_Error( ERR_FATAL, "%s has bad header", filename );
	}

	// round up to next power of 2 so all data operations can
	// be mask protected
	dataLength = header->dataLength + header->litLength + header->bssLength;
	for ( i = 0 ; dataLength > ( 1 << i ) ; i++ ) {
	}
	dataLength = 1 << i;

	// allocate zero filled space for initialized and uninitialized data
	vm->dataBase = Hunk_Alloc( dataLength, h_high );
	vm->dataMask = dataLength - 1;

	// copy the intialized data
	Com_Memcpy( vm->dataBase, (byte *)header + header->dataOffset, header->dataLength + header->litLength );

	// byte swap the longs
	for ( i = 0 ; i < header->dataLength ; i += 4 ) {
		*(int *)(vm->dataBase + i) = LittleLong( *(int *)(vm->dataBase + i ) );
	}

	// allocate space for the jump targets, which will be filled in by the compile/prep functions
	vm->instructionPointersLength = header->instructionCount * 4;
	vm->instructionPointers = Hunk_Alloc( vm->instructionPointersLength, h_high );

	// copy or compile the instructions
	vm->codeLength = header->codeLength;

	if ( interpret >= VMI_COMPILED ) {
		vm->compiled = qtrue;
		VM_Compile( vm, header );
	} else {
		vm->compiled = qfalse;
		VM_PrepareInterpreter( vm, header );
	}

	// free the original file
	FS_FreeFile( header );

	// load the map file
	VM_LoadSymbols( vm );

	// the stack is implicitly at the end of the image
	vm->programStack = vm->dataMask + 1;
	vm->stackBottom = vm->programStack - STACK_SIZE;

	Com_Printf("%s loaded in %d bytes on the hunk\n", module, remaining - Hunk_MemoryRemaining());
	VM_LogTraceEvent( "create %s %s", module, vm->dllHandle ? "native" : ( vm->compiled ? "compiled" : "interpreted" ) );

	return vm;
}

/*
==============
VM_Free
==============
*/
void VM_Free( vm_t *vm ) {
	VM_LogTraceEvent( "free %s", vm->name );

	if ( vm->dllHandle ) {
		Sys_UnloadDll( vm->dllHandle );
		Com_Memset( vm, 0, sizeof( *vm ) );
	}
#if 0	// now automatically freed by hunk
	if ( vm->codeBase ) {
		Z_Free( vm->codeBase );
	}
	if ( vm->dataBase ) {
		Z_Free( vm->dataBase );
	}
	if ( vm->instructionPointers ) {
		Z_Free( vm->instructionPointers );
	}
#endif
	Com_Memset( vm, 0, sizeof( *vm ) );

	currentVM = NULL;
	lastVM = NULL;
}

void VM_Clear(void) {
	int i;
	for (i=0;i<MAX_VM; i++) {
		if ( vmTable[i].dllHandle ) {
			Sys_UnloadDll( vmTable[i].dllHandle );
		}
		Com_Memset( &vmTable[i], 0, sizeof( vm_t ) );
	}
	currentVM = NULL;
	lastVM = NULL;
}

void *VM_ArgPtr( int intValue ) {
	if ( !intValue ) {
		return NULL;
	}
	// bk001220 - currentVM is missing on reconnect
	if ( currentVM==NULL )
	  return NULL;

	if ( currentVM->dllInterface ) {
		return (void *)(intptr_t)intValue;
	}
	if ( currentVM->entryPoint ) {
		return (void *)(currentVM->dataBase + intValue);
	}
	else {
		return (void *)(currentVM->dataBase + (intValue & currentVM->dataMask));
	}
}

void *VM_ExplicitArgPtr( vm_t *vm, int intValue ) {
	if ( !intValue ) {
		return NULL;
	}

	// bk010124 - currentVM is missing on reconnect here as well?
	if ( currentVM==NULL )
	  return NULL;

	//
	if ( vm->dllInterface ) {
		return (void *)(intptr_t)intValue;
	}
	if ( vm->entryPoint ) {
		return (void *)(vm->dataBase + intValue);
	}
	else {
		return (void *)(vm->dataBase + (intValue & vm->dataMask));
	}
}


/*
==============
VM_Call


Upon a system call, the stack will look like:

sp+32	parm1
sp+28	parm0
sp+24	return value
sp+20	return address
sp+16	local1
sp+14	local0
sp+12	arg1
sp+8	arg0
sp+4	return stack
sp		return address

An interpreted function will immediately execute
an OP_ENTER instruction, which will subtract space for
locals from sp
==============
*/
#define	MAX_STACK	256
#define	STACK_MASK	(MAX_STACK-1)

/*
=================
VM_CallNativeExports
=================
*/
static int VM_CallNativeExports( vm_t *vm, int callnum, const int *args ) {
	void	**dllExports;
	void	*exportFunc;

	if ( !vm->dllExports ) {
		Com_Error( ERR_FATAL, "VM_CallNativeExports: no exports for %s", vm->name );
	}

	dllExports = (void **)vm->dllExports;

	if ( !Q_stricmp( vm->name, "ui" ) ) {
		int uiExportIndex = callnum;

		Com_DPrintf( "VM_CallNativeExports(ui): callnum=%d api=%d iface=%d\n",
			callnum, vm->dllApiVersion, vm->dllInterface );

		if ( vm->dllInterface && vm->dllApiVersion > UI_API_VERSION ) {
			if ( callnum == UI_GETAPIVERSION ) {
				return vm->dllApiVersion;
			}
			uiExportIndex = callnum - 1;
		}

		switch ( callnum ) {
		case UI_GETAPIVERSION:
			exportFunc = dllExports[uiExportIndex];
			if ( !exportFunc ) {
				break;
			}
			return ((int (QDECL *)( void ))exportFunc)();
		case UI_INIT:
			exportFunc = dllExports[uiExportIndex];
			if ( !exportFunc ) {
				break;
			}
			((void (QDECL *)( qboolean ))exportFunc)( args[0] );
			return 0;
		case UI_SHUTDOWN:
			exportFunc = dllExports[uiExportIndex];
			if ( !exportFunc ) {
				break;
			}
			((void (QDECL *)( void ))exportFunc)();
			return 0;
		case UI_KEY_EVENT:
			exportFunc = dllExports[uiExportIndex];
			if ( !exportFunc ) {
				break;
			}
			((void (QDECL *)( int, int, int ))exportFunc)( args[0], args[1], args[2] );
			return 0;
		case UI_MOUSE_EVENT:
			exportFunc = dllExports[uiExportIndex];
			if ( !exportFunc ) {
				break;
			}
			((void (QDECL *)( int, int ))exportFunc)( args[0], args[1] );
			return 0;
		case UI_REFRESH:
			exportFunc = dllExports[uiExportIndex];
			if ( !exportFunc ) {
				break;
			}
			((void (QDECL *)( int ))exportFunc)( args[0] );
			return 0;
		case UI_IS_FULLSCREEN:
			exportFunc = dllExports[uiExportIndex];
			if ( !exportFunc ) {
				break;
			}
			return ((qboolean (QDECL *)( void ))exportFunc)();
		case UI_SET_ACTIVE_MENU:
			exportFunc = dllExports[uiExportIndex];
			if ( !exportFunc ) {
				break;
			}
			((void (QDECL *)( uiMenuCommand_t ))exportFunc)( args[0] );
			return 0;
		case UI_CONSOLE_COMMAND:
			exportFunc = dllExports[uiExportIndex];
			if ( !exportFunc ) {
				break;
			}
			return ((qboolean (QDECL *)( int ))exportFunc)( args[0] );
		case UI_DRAW_CONNECT_SCREEN:
			exportFunc = dllExports[uiExportIndex];
			if ( !exportFunc ) {
				break;
			}
			((void (QDECL *)( qboolean ))exportFunc)( args[0] );
			return 0;
		case UI_HASUNIQUECDKEY:
			exportFunc = dllExports[uiExportIndex];
			if ( !exportFunc ) {
				break;
			}
			return ((qboolean (QDECL *)( void ))exportFunc)();
		default:
			Com_Error( ERR_DROP, "VM_CallNativeExports: bad ui call %i", callnum );
		}
		Com_Error( ERR_DROP, "VM_CallNativeExports: missing ui export %i", callnum );
		return 0;
	}

	if ( !Q_stricmp( vm->name, "cgame" ) ) {
		switch ( callnum ) {
		case CG_INIT:
			exportFunc = dllExports[CG_INIT];
			if ( !exportFunc ) {
				break;
			}
			((void (QDECL *)( int, int, int ))exportFunc)( args[0], args[1], args[2] );
			return 0;
		case CG_SHUTDOWN:
			exportFunc = dllExports[CG_SHUTDOWN];
			if ( !exportFunc ) {
				break;
			}
			((void (QDECL *)( void ))exportFunc)();
			return 0;
		case CG_CONSOLE_COMMAND:
			exportFunc = dllExports[CG_CONSOLE_COMMAND];
			if ( !exportFunc ) {
				break;
			}
			return ((qboolean (QDECL *)( void ))exportFunc)();
		case CG_DRAW_ACTIVE_FRAME:
			exportFunc = dllExports[CG_DRAW_ACTIVE_FRAME];
			if ( !exportFunc ) {
				break;
			}
			((void (QDECL *)( int, stereoFrame_t, qboolean ))exportFunc)( args[0], args[1], args[2] );
			return 0;
		case CG_CROSSHAIR_PLAYER:
			exportFunc = dllExports[CG_CROSSHAIR_PLAYER];
			if ( !exportFunc ) {
				break;
			}
			return ((int (QDECL *)( void ))exportFunc)();
		case CG_LAST_ATTACKER:
			exportFunc = dllExports[CG_LAST_ATTACKER];
			if ( !exportFunc ) {
				break;
			}
			return ((int (QDECL *)( void ))exportFunc)();
		case CG_KEY_EVENT:
			exportFunc = dllExports[CG_KEY_EVENT];
			if ( !exportFunc ) {
				break;
			}
			((void (QDECL *)( int, qboolean ))exportFunc)( args[0], args[1] );
			return 0;
		case CG_MOUSE_EVENT:
			exportFunc = dllExports[CG_MOUSE_EVENT];
			if ( !exportFunc ) {
				break;
			}
			((void (QDECL *)( int, int ))exportFunc)( args[0], args[1] );
			return 0;
		case CG_EVENT_HANDLING:
			exportFunc = dllExports[CG_EVENT_HANDLING];
			if ( !exportFunc ) {
				break;
			}
			((void (QDECL *)( int ))exportFunc)( args[0] );
			return 0;
		default:
			Com_Error( ERR_DROP, "VM_CallNativeExports: bad cgame call %i", callnum );
		}
		Com_Error( ERR_DROP, "VM_CallNativeExports: missing cgame export %i", callnum );
		return 0;
	}

	if ( !Q_stricmp( vm->name, "qagame" ) ) {
		switch ( callnum ) {
		case GAME_INIT:
			exportFunc = dllExports[GAME_INIT];
			if ( !exportFunc ) {
				break;
			}
			((void (QDECL *)( int, int, int ))exportFunc)( args[0], args[1], args[2] );
			return 0;
		case GAME_SHUTDOWN:
			exportFunc = dllExports[GAME_SHUTDOWN];
			if ( !exportFunc ) {
				break;
			}
			((void (QDECL *)( void ))exportFunc)();
			return 0;
		case GAME_CLIENT_CONNECT:
			exportFunc = dllExports[GAME_CLIENT_CONNECT];
			if ( !exportFunc ) {
				break;
			}
			return (int)(intptr_t)((const char *(QDECL *)( int, qboolean, qboolean ))exportFunc)( args[0], args[1], args[2] );
		case GAME_CLIENT_BEGIN:
			exportFunc = dllExports[GAME_CLIENT_BEGIN];
			if ( !exportFunc ) {
				break;
			}
			((void (QDECL *)( int ))exportFunc)( args[0] );
			return 0;
		case GAME_CLIENT_USERINFO_CHANGED:
			exportFunc = dllExports[GAME_CLIENT_USERINFO_CHANGED];
			if ( !exportFunc ) {
				break;
			}
			((void (QDECL *)( int ))exportFunc)( args[0] );
			return 0;
		case GAME_CLIENT_DISCONNECT:
			exportFunc = dllExports[GAME_CLIENT_DISCONNECT];
			if ( !exportFunc ) {
				break;
			}
			((void (QDECL *)( int ))exportFunc)( args[0] );
			return 0;
		case GAME_CLIENT_COMMAND:
			exportFunc = dllExports[GAME_CLIENT_COMMAND];
			if ( !exportFunc ) {
				break;
			}
			((void (QDECL *)( int ))exportFunc)( args[0] );
			return 0;
		case GAME_CLIENT_THINK:
			exportFunc = dllExports[GAME_CLIENT_THINK];
			if ( !exportFunc ) {
				break;
			}
			((void (QDECL *)( int ))exportFunc)( args[0] );
			return 0;
		case GAME_RUN_FRAME:
			exportFunc = dllExports[GAME_RUN_FRAME];
			if ( !exportFunc ) {
				break;
			}
			((void (QDECL *)( int ))exportFunc)( args[0] );
			return 0;
		case GAME_CONSOLE_COMMAND:
			exportFunc = dllExports[GAME_CONSOLE_COMMAND];
			if ( !exportFunc ) {
				break;
			}
			return ((qboolean (QDECL *)( void ))exportFunc)();
		case BOTAI_START_FRAME:
			exportFunc = dllExports[BOTAI_START_FRAME];
			if ( !exportFunc ) {
				break;
			}
			((void (QDECL *)( int ))exportFunc)( args[0] );
			return 0;
		default:
			Com_Error( ERR_DROP, "VM_CallNativeExports: bad game call %i", callnum );
		}
		Com_Error( ERR_DROP, "VM_CallNativeExports: missing game export %i", callnum );
		return 0;
	}

	Com_Error( ERR_DROP, "VM_CallNativeExports: unknown module %s", vm->name );
	return 0;
}

int	QDECL VM_Call( vm_t *vm, int callnum, ... ) {
	vm_t	*oldVM;
	int		r;
	int i;
	int args[16];
	va_list ap;

	if ( !vm ) {
		Com_Error( ERR_FATAL, "VM_Call with NULL vm" );
	}

	oldVM = currentVM;
	currentVM = vm;
	lastVM = vm;
	VM_LogTraceEvent( "call %s %i", vm->name, callnum );

	if ( vm_debugLevel ) {
	  Com_Printf( "VM_Call( %i )\n", callnum );
	}

	// if we have a dll loaded, call it directly
	if ( vm->entryPoint || vm->dllExports ) {
		//rcg010207 -  see dissertation at top of VM_DllSyscall() in this file.
		va_start(ap, callnum);
		for (i = 0; i < sizeof (args) / sizeof (args[i]); i++) {
			args[i] = va_arg(ap, int);
		}
		va_end(ap);
	}

	if ( vm->entryPoint ) {
		r = vm->entryPoint( callnum,  args[0],  args[1],  args[2], args[3],
                            args[4],  args[5],  args[6], args[7],
                            args[8],  args[9], args[10], args[11],
                            args[12], args[13], args[14], args[15]);
	} else if ( vm->dllExports ) {
		r = VM_CallNativeExports( vm, callnum, args );
	} else if ( vm->compiled ) {
		r = VM_CallCompiled( vm, &callnum );
	} else {
		r = VM_CallInterpreted( vm, &callnum );
	}

	if ( oldVM != NULL ) // bk001220 - assert(currentVM!=NULL) for oldVM==NULL
	  currentVM = oldVM;
	return r;
}

//=================================================================

static int QDECL VM_ProfileSort( const void *a, const void *b ) {
	vmSymbol_t	*sa, *sb;

	sa = *(vmSymbol_t **)a;
	sb = *(vmSymbol_t **)b;

	if ( sa->profileCount < sb->profileCount ) {
		return -1;
	}
	if ( sa->profileCount > sb->profileCount ) {
		return 1;
	}
	return 0;
}

/*
==============
VM_VmProfile_f

==============
*/
void VM_VmProfile_f( void ) {
	vm_t		*vm;
	vmSymbol_t	**sorted, *sym;
	int			i;
	double		total;

	if ( !lastVM ) {
		return;
	}

	vm = lastVM;

	if ( !vm->numSymbols ) {
		return;
	}

	sorted = Z_Malloc( vm->numSymbols * sizeof( *sorted ) );
	sorted[0] = vm->symbols;
	total = sorted[0]->profileCount;
	for ( i = 1 ; i < vm->numSymbols ; i++ ) {
		sorted[i] = sorted[i-1]->next;
		total += sorted[i]->profileCount;
	}

	qsort( sorted, vm->numSymbols, sizeof( *sorted ), VM_ProfileSort );

	for ( i = 0 ; i < vm->numSymbols ; i++ ) {
		int		perc;

		sym = sorted[i];

		perc = 100 * (float) sym->profileCount / total;
		Com_Printf( "%2i%% %9i %s\n", perc, sym->profileCount, sym->symName );
		sym->profileCount = 0;
	}

	Com_Printf("    %9.0f total\n", total );

	Z_Free( sorted );
}

/*
==============
VM_VmInfo_f

==============
*/
void VM_VmInfo_f( void ) {
	vm_t	*vm;
	int		i;

	Com_Printf( "Registered virtual machines:\n" );
	for ( i = 0 ; i < MAX_VM ; i++ ) {
		vm = &vmTable[i];
		if ( !vm->name[0] ) {
			break;
		}
		Com_Printf( "%s : ", vm->name );
		if ( vm->dllHandle ) {
			Com_Printf( "native\n" );
			continue;
		}
		if ( vm->compiled ) {
			Com_Printf( "compiled on load\n" );
		} else {
			Com_Printf( "interpreted\n" );
		}
		Com_Printf( "    code length : %7i\n", vm->codeLength );
		Com_Printf( "    table length: %7i\n", vm->instructionPointersLength );
		Com_Printf( "    data length : %7i\n", vm->dataMask + 1 );
	}
}

/*
===============
VM_LogSyscalls

Insert calls to this while debugging the vm compiler
===============
*/
void VM_LogSyscalls( int *args ) {
	static	int		callnum;
	static	FILE	*f;

	if ( !f ) {
		f = fopen("syscalls.log", "w" );
	}
	callnum++;
	fprintf(f, "%i: %i (%i) = %i %i %i %i\n", callnum, args - (int *)currentVM->dataBase,
		args[0], args[1], args[2], args[3], args[4] );
}



#ifdef oDLL_ONLY // bk010215 - for DLL_ONLY dedicated servers/builds w/o VM
int	VM_CallCompiled( vm_t *vm, int *args ) {
  return(0); 
}

void VM_Compile( vm_t *vm, vmHeader_t *header ) {}
#endif // DLL_ONLY
