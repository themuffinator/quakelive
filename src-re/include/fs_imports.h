#ifndef QLR_FS_IMPORTS_H
#define QLR_FS_IMPORTS_H

#include <stddef.h>

typedef struct qlr_fs_imports_s {
	int (*fopen_file_by_mode)( const char *qpath, int *handle, int mode );
	int (*sv_fopen_file_read)( const char *filename, int *handle );
	int (*sv_fopen_file_write)( const char *filename );
	int (*read_file)( void *buffer, int length, int handle );
	int (*write_file)( const void *buffer, int length, int handle );
	void (*close_file)( int handle );
	int (*get_file_list)( const char *path, const char *extension, char *list, int buffer_size );
	int (*seek_file)( int handle, long offset, int origin );
	const char *(*loaded_pak_checksums)( void );
	const char *(*loaded_pak_pure_checksums)( void );
	const char *(*referenced_pak_checksums)( void );
	const char *(*referenced_pak_pure_checksums)( void );
	char *(*build_os_path)( const char *base, const char *game, const char *qpath );
} qlr_fs_imports_t;

extern const qlr_fs_imports_t qlr_fs_imports;

#endif /* QLR_FS_IMPORTS_H */
