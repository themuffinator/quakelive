from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _extract_function_block(text: str, signature: str) -> str:
    start = text.find(signature)
    if start == -1:
        raise AssertionError(f"function signature not found: {signature}")

    brace_start = text.find("{", start)
    if brace_start == -1:
        raise AssertionError(f"opening brace not found for: {signature}")

    depth = 0
    for index in range(brace_start, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]

    raise AssertionError(f"unterminated function block for: {signature}")


def test_client_workshop_bootstrap_reconstructs_retail_join_and_completion_owners() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

    refresh_cvars_block = _extract_function_block(cl_main, "static void CL_RefreshPlatformServiceCvars( void ) {")
    workshop_log_block = _extract_function_block(cl_main, "static void CL_LogWorkshopLifecycle( const char *stage, const char *detail ) {")
    workshop_service_support_block = _extract_function_block(cl_main, "static qboolean CL_WorkshopServiceSupportsSteamBootstrap( void ) {")
    init_block = _extract_function_block(cl_main, "void CL_InitDownloads(void) {")
    frame_block = _extract_function_block(cl_main, "void CL_Frame ( int msec ) {")
    workshop_frame_block = _extract_function_block(cl_main, "static void CL_Workshop_Frame( void ) {")
    request_download_block = _extract_function_block(cl_main, "static qboolean CL_Workshop_RequestDownload( int itemIndex ) {")
    advance_queue_block = _extract_function_block(cl_main, "static qboolean CL_Workshop_AdvanceDownloadQueue( void ) {")
    finalize_block = _extract_function_block(cl_main, "static qboolean CL_Workshop_FinalizeInstalledItem( int itemIndex ) {")
    fail_block = _extract_function_block(cl_main, "static qboolean CL_Workshop_FailActiveDownload( void ) {")
    downloads_settled_block = _extract_function_block(cl_main, "static qboolean CL_Workshop_DownloadsSettled( void ) {")
    workshop_begin_block = _extract_function_block(cl_main, "static qboolean CL_Workshop_BeginBootstrap( void ) {")
    workshop_callback_init_block = _extract_function_block(
        cl_main, "static qboolean CL_Steam_RegisterWorkshopCallbacks( const char *workshopProvider, const char *workshopPolicy ) {"
    )
    callback_shutdown_block = _extract_function_block(cl_main, "static void CL_Steam_ShutdownCallbacks( void ) {")
    item_installed_block = _extract_function_block(cl_main, "static void CL_Steam_Workshop_OnItemInstalled( void *context, const ql_steam_item_installed_t *event ) {")
    download_result_block = _extract_function_block(
        cl_main, "static void CL_Steam_Workshop_OnDownloadItemResult( void *context, const ql_steam_download_item_result_t *event ) {"
    )

    assert "#define CL_STEAM_WORKSHOP_ITEMS_CONFIGSTRING 0x2cb" in cl_main
    assert 'Cvar_Set( "cl_workshopProvider", CL_GetWorkshopServiceProviderLabel() );' in refresh_cvars_block
    assert 'Cvar_Set( "cl_workshopPolicy", CL_GetWorkshopServicePolicyLabel() );' in refresh_cvars_block
    assert 'Com_Printf( "Workshop %s via %s [%s]: %s\\n",' in workshop_log_block
    assert "CL_GetWorkshopServiceProviderLabel()" in workshop_log_block
    assert "CL_GetWorkshopServicePolicyLabel()" in workshop_log_block
    assert 'return ( strstr( provider, "Steam UGC" ) != NULL );' in workshop_service_support_block
    assert 'Com_Printf( "Server requires the following workshop items: %s\\n", workshopItems );' in workshop_begin_block
    assert "CL_GetWorkshopServiceProviderLabel();" not in workshop_begin_block
    assert "CL_GetWorkshopServicePolicyLabel();" not in workshop_begin_block
    assert "CL_WorkshopServiceSupportsSteamBootstrap()" in workshop_begin_block
    assert 'CL_LogWorkshopLifecycle( "bootstrap-unavailable", "required items unavailable; keeping compatibility-only fallback" );' in workshop_begin_block
    assert 'CL_LogWorkshopLifecycle( "bootstrap-begin", detail );' in workshop_begin_block
    assert 'CL_LogWorkshopLifecycle( "bootstrap-truncate", detail );' in workshop_begin_block
    assert 'if ( CL_Workshop_RequestDownload( itemIndex ) ) {' in workshop_begin_block
    assert "item->requestNumber = ++requestNumber;" in workshop_begin_block
    assert 'cl_steamWorkshopDownloadState.downloadsRequested = qtrue;' in workshop_begin_block
    assert "CL_Workshop_SetDownloadRequestCvars( itemIndex );" in workshop_begin_block
    assert 'Com_sprintf( downloadName, sizeof( downloadName ), "Workshop item %i of %i", item->requestNumber, cl_steamWorkshopDownloadState.totalItems );' in cl_main
    assert "CL_Workshop_ClearBootstrapState( qtrue );" in init_block
    assert "if ( CL_Workshop_BeginBootstrap() ) {" in init_block
    assert "CL_Workshop_Frame();" in frame_block
    assert frame_block.index("CL_Workshop_Frame();") < frame_block.index("CL_SendCmd();")
    assert frame_block.index("CL_Workshop_Frame();") < frame_block.index("CL_CheckForResend();")
    assert 'CL_LogWorkshopLifecycle( "request-download", detail );' in request_download_block
    assert '"Workshop item %llu: in cache."' in request_download_block
    assert '"Workshop item %llu: requesting download."' in request_download_block
    assert '"Workshop item %llu: queueing download."' in request_download_block
    assert "CL_Workshop_FinalizeInstalledItem( itemIndex );" in request_download_block
    assert "cl_steamWorkshopDownloadState.queueActive = qtrue;" in request_download_block
    assert "item->queued = qtrue;" in request_download_block
    assert '"Workshop item %llu: was queued, requesting download."' in advance_queue_block
    assert "CL_Workshop_ClearActiveDownload();" in advance_queue_block
    assert "item->queued = qfalse;" in advance_queue_block
    assert "item->downloadRequested = qtrue;" in advance_queue_block
    assert 'CL_LogWorkshopLifecycle( "item-complete", detail );' in finalize_block
    assert '"Steamworks download complete: %llu"' in finalize_block
    assert "return CL_Workshop_AdvanceDownloadQueue();" in finalize_block
    assert "item->completed = qtrue;" in fail_block
    assert 'CL_LogWorkshopLifecycle( "item-failed", detail );' not in fail_block
    assert "return CL_Workshop_AdvanceDownloadQueue();" in fail_block
    assert 'CL_LogWorkshopLifecycle( "queue-complete", "Download completed for all steamworks items" );' in downloads_settled_block
    assert 'if ( CL_Workshop_AdvanceDownloadQueue() ) {' in downloads_settled_block
    assert "FS_Restart( clc.checksumFeed );" in workshop_frame_block
    assert 'Com_Printf( "Steamworks downloads complete - FS restart is required\\n" );' in workshop_frame_block
    assert 'Com_Printf( "Steamworks downloads complete\\n" );' in workshop_frame_block
    assert "FS_ComparePaks( missingfiles, sizeof( missingfiles ), qfalse )" in workshop_frame_block
    assert "CL_DownloadsComplete();" in workshop_frame_block
    assert 'Com_Printf( "WARNING: Missing pk3s referenced by the server:\\n%s\\n"' in workshop_frame_block
    assert "QL_Steamworks_RegisterWorkshopCallbacks( &workshopBindings )" in workshop_callback_init_block
    assert 'CL_LogWorkshopLifecycle( "callback-bootstrap", detail );' in workshop_callback_init_block
    assert '"callbacks unavailable; keeping polling fallback (%s [%s])"' in workshop_callback_init_block
    assert "QL_Steamworks_UnregisterWorkshopCallbacks();" in callback_shutdown_block
    assert 'CL_LogWorkshopLifecycle( "callback-item-installed", detail );' in item_installed_block
    assert 'CL_LogWorkshopLifecycle( "callback-item-installed", "ignored null callback payload" );' in item_installed_block
    assert 'CL_LogWorkshopLifecycle( "callback-item-installed", "ignored installed callback without active download state" );' in item_installed_block
    assert '"OnDownloadItemResult skip, invalid app id %d"' in item_installed_block
    assert '"ignored installed callback for untracked item %llu"' in item_installed_block
    assert '"installed item %llu request=%d"' in item_installed_block
    assert "CL_Workshop_FinalizeInstalledItem( itemIndex );" in item_installed_block
    assert 'CL_LogWorkshopLifecycle( "callback-download-result", detail );' in download_result_block
    assert 'CL_LogWorkshopLifecycle( "callback-download-result", "ignored null callback payload" );' in download_result_block
    assert 'CL_LogWorkshopLifecycle( "callback-download-result", "ignored download callback without active download state" );' in download_result_block
    assert 'CL_LogWorkshopLifecycle( "callback-download-result", "ignored download callback without active item index" );' in download_result_block
    assert '"OnDownloadItemResult skip, invalid app id %d"' in download_result_block
    assert '"OnDownloadItemResult skip, not the active download %llu"' in download_result_block
    assert '"Download item %llu failed with EResult code %i"' in download_result_block
    assert "CL_Workshop_FinalizeInstalledItem( cl_steamWorkshopDownloadState.activeItemIndex );" in download_result_block
    assert "CL_Workshop_FailActiveDownload();" in download_result_block
    assert "CL_Workshop_AdvanceDownloadQueue();" not in download_result_block


def test_client_workshop_progress_owner_is_exposed_for_ui_imports() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

    download_info_block = _extract_function_block(
        cl_main,
        "qboolean CL_GetWorkshopDownloadInfo( unsigned int itemIdLow, unsigned int itemIdHigh, unsigned long long *outDownloaded, unsigned long long *outTotal ) {",
    )

    assert "cl_steamWorkshopDownloadState.activeItemIndex < 0" in download_info_block
    assert "item->itemIdLow != itemIdLow || item->itemIdHigh != itemIdHigh" in download_info_block
    assert "*outDownloaded = (unsigned long long)cl_steamWorkshopDownloadState.downloadedBytes;" in download_info_block
    assert "*outTotal = (unsigned long long)cl_steamWorkshopDownloadState.totalBytes;" in download_info_block


def test_ui_item_download_import_uses_retained_client_workshop_state() -> None:
    cl_ui = (REPO_ROOT / "src/code/client/cl_ui.c").read_text(encoding="utf-8")

    download_info_block = _extract_function_block(
        cl_ui,
        "static void QDECL QL_UI_trap_GetItemDownloadInfo( unsigned int itemIdLow, unsigned int itemIdHigh, unsigned long long *outDownloaded, unsigned long long *outTotal ) {",
    )

    assert "CL_GetWorkshopDownloadInfo( itemIdLow, itemIdHigh, &downloaded, &total )" in download_info_block
    assert "SteamUGC_GetItemDownloadInfo( itemIdLow, itemIdHigh, &downloaded, &total );" in download_info_block
    assert "clc.downloadCount" not in download_info_block
    assert "clc.downloadSize" not in download_info_block


def test_reverse_engineering_workshop_notes_track_current_progress_and_callback_owner_split() -> None:
    round05 = (
        REPO_ROOT / "docs" / "reverse-engineering" / "quakelive_steam_mapping_round_05.md"
    ).read_text(encoding="utf-8")
    round14 = (
        REPO_ROOT / "docs" / "reverse-engineering" / "quakelive_steam_mapping_round_14.md"
    ).read_text(encoding="utf-8")
    client_plan = (
        REPO_ROOT / "docs" / "reverse-engineering" / "client-full-parity-audit-and-implementation-plan-2026-04-09.md"
    ).read_text(encoding="utf-8")
    client_cvars = (REPO_ROOT / "docs" / "client_cvars.md").read_text(encoding="utf-8")
    implementation_plan = (REPO_ROOT / "IMPLEMENTATION_PLAN.md").read_text(encoding="utf-8")

    assert "consulting retained client workshop state first and then falling back to `QL_Steamworks_GetItemDownloadInfo`, the retained wrapper over the same low/high-word `SteamUGC_GetItemDownloadInfo` slot" in round05
    assert "parses `cl_downloadItem` and calls offset `0x180` with the resulting `(itemIdLow, itemIdHigh, &downloaded, &total)` words" in round14
    assert "`cl_ui.c` reconstructs import `96` as `QL_UI_trap_GetItemDownloadInfo`" in round14
    assert "retained client workshop state before falling back to `QL_Steamworks_GetItemDownloadInfo`, the retained platform wrapper over `SteamUGC_GetItemDownloadInfo` reached from the parsed low/high words" in round14
    assert "mirrored in retained `cl_ui.c` as a retained-state-first bridge that falls back to `QL_Steamworks_GetItemDownloadInfo`" in round14
    assert "consults retained client workshop state first before falling back to `QL_Steamworks_GetItemDownloadInfo`, the retained wrapper over the retail `SteamUGC_GetItemDownloadInfo` low/high-word slot keyed by the parsed `cl_downloadItem` words, instead of legacy byte counters" in client_plan
    assert "seeds the retail-facing `cl_downloadItem` / `cl_downloadName` / `cl_downloadTime` request surface from that retained state" in client_plan
    assert "imports workshop download progress from retained client state before falling back to `QL_Steamworks_GetItemDownloadInfo`, the retained wrapper over the retail `SteamUGC_GetItemDownloadInfo` low/high-word slot" in client_plan
    assert "routes installed-item completion plus download-result failure through the shared queue-pop owner" in client_plan
    assert "seeds `cl_downloadItem` / `cl_downloadName` / `cl_downloadTime` from that state" in client_plan
    assert "only falls back to `QL_Steamworks_GetItemDownloadInfo`, the retained wrapper over the retail `SteamUGC_GetItemDownloadInfo` low/high-word slot" in client_plan
    assert "consumes `ItemInstalled` / `DownloadItemResult` through shared finalize/failure helpers that tail into `SteamWorkshop_AdvanceDownloadQueue`" in client_plan
    assert "reconstructed client/workshop state first, then the recovered `GetItemDownloadInfo` low/high-word bridge" in client_plan
    assert "state first and only then falls back to `QL_Steamworks_GetItemDownloadInfo`," in implementation_plan
    assert "`SteamUGC_GetItemDownloadInfo` slot." in implementation_plan
    assert "Kept the then-retained UI-facing `cl_downloadCount` / `cl_downloadSize`" in implementation_plan
    assert "temp-cvar updates intact around that narrower helper contract." in implementation_plan
    assert "Workshop/bootstrap request bookkeeping (`cl_downloadItem`, `cl_downloadName`, `cl_downloadTime`) matches the recovered `CL_InitDownloads` and `uix86` surface" in client_cvars
    assert "reads `cl_downloadItem`, calls the native `GetItemDownloadInfo` probe with the parsed item-ID low/high words, and consults `cl_downloadTime`" in client_cvars
    assert "`cl_downloadCount` and `cl_downloadSize` still exist because Quake Live UI strings reference them" in client_cvars
