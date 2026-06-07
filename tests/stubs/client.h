#ifndef CLIENT_H
#define CLIENT_H

#include <stdarg.h>
#include <stdint.h>
#include "q_shared.h"

qboolean CL_OnlineServicesEnabled( void );
qboolean CL_SteamServicesEnabled( void );
unsigned long long SteamClient_GetSteamID( void );
int SteamClient_GetAuthSessionTicket( char *ticketBuffer, int ticketBufferSize );
qboolean SteamClient_CancelAuthTicket( void );
qboolean SteamApps_BIsSubscribedApp( unsigned int appId );
qboolean SteamUGC_GetItemDownloadInfo( unsigned int itemIdLow, unsigned int itemIdHigh, unsigned long long *outDownloaded, unsigned long long *outTotal );
qboolean SteamUtils_GetIPCountry( char *buffer, size_t bufferSize );

#endif /* CLIENT_H */
