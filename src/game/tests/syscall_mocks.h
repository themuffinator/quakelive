#ifndef GAME_TESTS_SYSCALL_MOCKS_H
#define GAME_TESTS_SYSCALL_MOCKS_H

#if defined(__has_include)
#if __has_include("q_shared.h")
#include "q_shared.h"
#elif __has_include("../code/game/q_shared.h")
#include "../code/game/q_shared.h"
#elif __has_include("../../code/game/q_shared.h")
#include "../../code/game/q_shared.h"
#else
#error "Unable to locate q_shared.h for syscall mocks"
#endif
#else
#include "../../code/game/q_shared.h"
#endif

#include "../ql_game_types.h"

#include <stdarg.h>

typedef int (*game_test_syscall_handler_t)(int command, va_list args, void *user);

// Binds the handler used by g_syscalls.c. Passing NULL installs the default printer-based handler.
void GT_InitSyscallMocks(game_test_syscall_handler_t handler, void *user);

// Resets the dispatcher to the default handler that logs to stdout/stderr.
void GT_ResetSyscallMocks(void);

// Default implementation that writes G_PRINT/G_ERROR to stdout/stderr and ignores other commands.
int GT_DefaultSyscallHandler(int command, va_list args, void *user);

#endif // GAME_TESTS_SYSCALL_MOCKS_H
