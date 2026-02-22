/*
=============
fs_imports.h

Filesystem import table shared across native syscall shims.
=============
*/

#ifndef QLR_FS_IMPORTS_H
#define QLR_FS_IMPORTS_H

#include "../../src/code/game/q_shared.h"
#include <stddef.h>

typedef struct qlr_fs_imports_s {
	int (*fopen_file_by_mode)(const char *path, fileHandle_t *handle, fsMode_t mode);
	qboolean (*fopen_web_file_read)(const char *path, fileHandle_t *handle, char *resolved, size_t resolved_len);
	int (*filelength)(fileHandle_t handle);
	int (*read)(void *buffer, int len, fileHandle_t handle);
	int (*write)(const void *buffer, int len, fileHandle_t handle);
	void (*fclose_file)(fileHandle_t handle);
	int (*get_file_list)(const char *path, const char *extension, char *listbuf, int bufsize);
	int (*seek)(fileHandle_t handle, long offset, int origin);
	char *(*build_os_path)(const char *base, const char *game, const char *qpath);
	const char *(*loaded_pak_checksums)(void);
	const char *(*loaded_pak_pure_checksums)(void);
	const char *(*referenced_pak_checksums)(void);
	const char *(*referenced_pak_pure_checksums)(void);
} qlr_fs_imports_t;

extern const qlr_fs_imports_t qlr_fs_imports;

#endif /* QLR_FS_IMPORTS_H */
