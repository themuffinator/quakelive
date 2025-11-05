#include "syscall_mocks.h"

#ifndef Q3_VM
#include <stdio.h>
#endif

static game_test_syscall_handler_t gt_syscall_handler = GT_DefaultSyscallHandler;
static void *gt_syscall_user = NULL;

static int QDECL GT_Dispatcher(int command, ...) {
    va_list args;
    int result = 0;

    va_start(args, command);
    if (gt_syscall_handler) {
        result = gt_syscall_handler(command, args, gt_syscall_user);
    }
    va_end(args);
    return result;
}

#ifdef Q3_VM
#define GAME_TESTS_WAS_Q3_VM 1
#undef Q3_VM
#endif
#include "../../code/game/g_syscalls.c"
#ifdef GAME_TESTS_WAS_Q3_VM
#define Q3_VM 1
#endif

void GT_InitSyscallMocks(game_test_syscall_handler_t handler, void *user) {
    gt_syscall_handler = handler ? handler : GT_DefaultSyscallHandler;
    gt_syscall_user = user;
    dllEntry(GT_Dispatcher);
}

void GT_ResetSyscallMocks(void) {
    GT_InitSyscallMocks(NULL, NULL);
}

int GT_DefaultSyscallHandler(int command, va_list args, void *user) {
    (void)user;

    switch (command) {
        case G_PRINT: {
            const char *message = va_arg(args, const char *);
#ifndef Q3_VM
            if (message) {
                fputs(message, stdout);
            }
#else
            (void)message;
#endif
            return 0;
        }
        case G_ERROR: {
            const char *message = va_arg(args, const char *);
#ifndef Q3_VM
            if (message) {
                fputs(message, stderr);
                fputc('\n', stderr);
            }
#else
            (void)message;
#endif
            return 0;
        }
        default:
            return 0;
    }
}
