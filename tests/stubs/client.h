#ifndef CLIENT_H
#define CLIENT_H

#include <stdarg.h>

void Com_Printf( const char *fmt, ... );
void Com_sprintf( char *dest, int size, const char *fmt, ... );
int Q_stricmp( const char *s1, const char *s2 );
int Q_stricmpn( const char *s1, const char *s2, int n );
void Q_strncpyz( char *dest, const char *src, int destsize );

#endif /* CLIENT_H */
