#ifndef QLR_NATIVE_SHIM_H
#define QLR_NATIVE_SHIM_H

#include <stddef.h>
#include <stdint.h>

/*
 * Logging helpers used by the native prototypes to capture the data exchanged
 * with the VM-facing glue code.  The shim keeps a simple append-only log under
 * logs/re/native-shim.log for human-readable traces and mirrors syscall
 * contracts to logs/syscall_contract.log so the data can be diffed against the
 * QVM runtime.
 */

#ifdef __cplusplus
extern "C" {
#endif

void qlr_native_shim_reset_log(void);
void qlr_native_shim_close(void);
void qlr_native_shim_flush(void);
void qlr_native_shim_logf(const char *module, const char *symbol, const char *fmt, ...);
void qlr_native_shim_log_syscall(const char *module, int command, size_t argc, const intptr_t *argv);

#ifdef __cplusplus
}
#endif

#endif /* QLR_NATIVE_SHIM_H */
