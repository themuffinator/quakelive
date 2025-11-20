#include "qcommon.h"

#include "../../src-re/include/fs_imports.h"

extern char *FS_BuildOSPath( const char *base, const char *game, const char *qpath );

	const qlr_fs_imports_t qlr_fs_imports = {
	.fopen_file_by_mode = FS_FOpenFileByMode,
	.sv_fopen_file_read = FS_SV_FOpenFileRead,
	.sv_fopen_file_write = FS_SV_FOpenFileWrite,
	.read_file = FS_Read2,
	.write_file = FS_Write,
	.close_file = FS_FCloseFile,
	.get_file_list = FS_GetFileList,
	.seek_file = FS_Seek,
	.loaded_pak_checksums = FS_LoadedPakChecksums,
	.loaded_pak_pure_checksums = FS_LoadedPakPureChecksums,
	.referenced_pak_checksums = FS_ReferencedPakChecksums,
	.referenced_pak_pure_checksums = FS_ReferencedPakPureChecksums,
	.build_os_path = FS_BuildOSPath
};
