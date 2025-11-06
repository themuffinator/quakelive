#include "native_shim.h"

#include <errno.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_WIN32)
#include <direct.h>
#define QLR_NATIVE_MKDIR(path) _mkdir(path)
#else
#include <sys/stat.h>
#include <sys/types.h>
#define QLR_NATIVE_MKDIR(path) mkdir(path, 0755)
#endif

static const char *const qlr_native_log_path = "logs/re/native-shim.log";
static const char *const qlr_native_contract_path = "logs/syscall_contract.log";
static FILE *qlr_native_log_handle = NULL;
static FILE *qlr_native_contract_handle = NULL;
static bool qlr_native_log_truncated = false;
static bool qlr_native_contract_truncated = false;

static bool qlr_native_shim_create_directory(const char *path) {
    if (!path || *path == '\0') {
        return false;
    }

    char buffer[512];
    size_t length = strlen(path);
    if (length >= sizeof(buffer)) {
        return false;
    }
    memcpy(buffer, path, length + 1);

    char *cursor = buffer;
    if (*cursor == '/') {
        ++cursor;
    }

    for (; *cursor; ++cursor) {
        if (*cursor != '/' && *cursor != '\\') {
            continue;
        }
        char saved = *cursor;
        *cursor = '\0';
        if (buffer[0] != '\0' && QLR_NATIVE_MKDIR(buffer) != 0 && errno != EEXIST) {
            *cursor = saved;
            return false;
        }
        *cursor = saved;
    }

    if (QLR_NATIVE_MKDIR(buffer) != 0 && errno != EEXIST) {
        return false;
    }
    return true;
}

static bool qlr_native_shim_ensure_directory_for_path(const char *path) {
    if (!path) {
        return false;
    }

    const char *slash = strrchr(path, '/');
    if (!slash) {
        return true;
    }

    char directory[512];
    size_t dir_len = (size_t)(slash - path);
    if (dir_len >= sizeof(directory)) {
        return false;
    }
    memcpy(directory, path, dir_len);
    directory[dir_len] = '\0';

    if (!qlr_native_shim_create_directory(directory)) {
        return false;
    }

    return true;
}

static FILE *qlr_native_shim_open_log(void) {
    if (qlr_native_log_handle) {
        return qlr_native_log_handle;
    }

    if (!qlr_native_shim_ensure_directory_for_path(qlr_native_log_path)) {
        return NULL;
    }

    if (!qlr_native_log_truncated) {
        FILE *truncate = fopen(qlr_native_log_path, "w");
        if (truncate) {
            fclose(truncate);
        }
        qlr_native_log_truncated = true;
    }

    qlr_native_log_handle = fopen(qlr_native_log_path, "a");
    if (qlr_native_log_handle) {
        setvbuf(qlr_native_log_handle, NULL, _IONBF, 0);
    }
    return qlr_native_log_handle;
}

static FILE *qlr_native_shim_open_contract_log(void) {
    if (qlr_native_contract_handle) {
        return qlr_native_contract_handle;
    }

    if (!qlr_native_shim_ensure_directory_for_path(qlr_native_contract_path)) {
        return NULL;
    }

    if (!qlr_native_contract_truncated) {
        FILE *truncate = fopen(qlr_native_contract_path, "w");
        if (truncate) {
            fclose(truncate);
        }
        qlr_native_contract_truncated = true;
    }

    qlr_native_contract_handle = fopen(qlr_native_contract_path, "a");
    if (qlr_native_contract_handle) {
        setvbuf(qlr_native_contract_handle, NULL, _IONBF, 0);
    }
    return qlr_native_contract_handle;
}

void qlr_native_shim_reset_log(void) {
    if (qlr_native_log_handle) {
        fclose(qlr_native_log_handle);
        qlr_native_log_handle = NULL;
    }
    qlr_native_log_truncated = false;
    qlr_native_shim_open_log();

    if (qlr_native_contract_handle) {
        fclose(qlr_native_contract_handle);
        qlr_native_contract_handle = NULL;
    }
    qlr_native_contract_truncated = false;
    qlr_native_shim_open_contract_log();
}

void qlr_native_shim_close(void) {
    if (qlr_native_log_handle) {
        fclose(qlr_native_log_handle);
        qlr_native_log_handle = NULL;
    }
    if (qlr_native_contract_handle) {
        fclose(qlr_native_contract_handle);
        qlr_native_contract_handle = NULL;
    }
}

void qlr_native_shim_flush(void) {
    if (qlr_native_log_handle) {
        fflush(qlr_native_log_handle);
    }
    if (qlr_native_contract_handle) {
        fflush(qlr_native_contract_handle);
    }
}

static void qlr_native_shim_write_prefix(FILE *stream, const char *module, const char *symbol) {
    if (!stream) {
        return;
    }
    if (!module) {
        module = "?";
    }
    if (!symbol) {
        symbol = "?";
    }
    fprintf(stream, "[%s] %s: ", module, symbol);
}

void qlr_native_shim_logf(const char *module, const char *symbol, const char *fmt, ...) {
    FILE *stream = qlr_native_shim_open_log();
    if (!stream) {
        return;
    }

    qlr_native_shim_write_prefix(stream, module, symbol);

    va_list args;
    va_start(args, fmt);
    if (fmt && *fmt) {
        vfprintf(stream, fmt, args);
    }
    va_end(args);
    fputc('\n', stream);
}

void qlr_native_shim_log_syscall(const char *module, int command, size_t argc, const intptr_t *argv) {
    FILE *stream = qlr_native_shim_open_log();
    if (stream) {
        qlr_native_shim_write_prefix(stream, module, "syscall");
        fprintf(stream, "cmd=0x%X argc=%zu", command, argc);
        for (size_t index = 0; index < argc; ++index) {
            fprintf(stream, " arg%zu=0x%lX", index, (unsigned long)argv[index]);
        }
        fputc('\n', stream);
    }

    FILE *contract = qlr_native_shim_open_contract_log();
    if (!contract) {
        return;
    }

    const size_t max_args = 16;
    size_t count = argc < max_args ? argc : max_args;

    if (!module) {
        module = "unknown";
    }

    fprintf(contract, "shim-native %s", module);
    for (size_t index = 0; index < count; ++index) {
        unsigned int value = (unsigned int)(uintptr_t)argv[index];
        fprintf(contract, " %08x", value);
    }
    fputc('\n', contract);
}
