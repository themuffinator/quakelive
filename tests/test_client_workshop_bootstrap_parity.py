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

    init_block = _extract_function_block(cl_main, "void CL_InitDownloads(void) {")
    frame_block = _extract_function_block(cl_main, "void CL_Frame ( int msec ) {")
    workshop_frame_block = _extract_function_block(cl_main, "static void CL_Workshop_Frame( void ) {")
    workshop_begin_block = _extract_function_block(cl_main, "static qboolean CL_Workshop_BeginBootstrap( void ) {")
    callback_init_block = _extract_function_block(cl_main, "static void CL_Steam_InitCallbacks( void ) {")
    callback_shutdown_block = _extract_function_block(cl_main, "static void CL_Steam_ShutdownCallbacks( void ) {")
    item_installed_block = _extract_function_block(cl_main, "static void CL_Steam_Workshop_OnItemInstalled( void *context, const ql_steam_item_installed_t *event ) {")
    download_result_block = _extract_function_block(
        cl_main, "static void CL_Steam_Workshop_OnDownloadItemResult( void *context, const ql_steam_download_item_result_t *event ) {"
    )

    assert "#define CL_STEAM_WORKSHOP_ITEMS_CONFIGSTRING 0x2cb" in cl_main
    assert "Server requires the following workshop items: %s\\n" in workshop_begin_block
    assert "QL_Steamworks_GetItemState( itemIdLow, itemIdHigh ) & CL_STEAM_WORKSHOP_ITEM_STATE_INSTALLED" in workshop_begin_block
    assert 'Com_sprintf( downloadName, sizeof( downloadName ), "Workshop item %i of %i", item->requestNumber, cl_steamWorkshopDownloadState.totalItems );' in cl_main
    assert "CL_Workshop_ClearBootstrapState( qtrue );" in init_block
    assert "if ( CL_Workshop_BeginBootstrap() ) {" in init_block
    assert "CL_Workshop_Frame();" in frame_block
    assert frame_block.index("CL_Steam_Frame();") < frame_block.index("CL_Workshop_Frame();")
    assert frame_block.index("CL_Workshop_Frame();") < frame_block.index("CL_CheckForResend();")
    assert "FS_Restart( clc.checksumFeed );" in workshop_frame_block
    assert "FS_ComparePaks( missingfiles, sizeof( missingfiles ), qfalse )" in workshop_frame_block
    assert "CL_DownloadsComplete();" in workshop_frame_block
    assert "QL_Steamworks_RegisterWorkshopCallbacks( &workshopBindings )" in callback_init_block
    assert "Steam workshop callbacks unavailable; keeping polling fallback\\n" in callback_init_block
    assert "QL_Steamworks_UnregisterWorkshopCallbacks();" in callback_shutdown_block
    assert "OnItemInstalled skip, invalid app id %d\\n" in item_installed_block
    assert "CL_Workshop_FinalizeInstalledItem( itemIndex );" in item_installed_block
    assert "OnDownloadItemResult skip, invalid app id %d\\n" in download_result_block
    assert "OnDownloadItemResult skip, not the active download %llu\\n" in download_result_block
    assert "CL_Workshop_FailActiveDownload( event->result );" in download_result_block


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
        "static void QDECL QL_UI_trap_GetItemDownloadInfo( unsigned int arg1, unsigned int arg2, unsigned long long *outDownloaded, unsigned long long *outTotal ) {",
    )

    assert "CL_GetWorkshopDownloadInfo( arg1, arg2, &downloaded, &total )" in download_info_block
    assert "QL_Steamworks_GetItemDownloadInfo( arg1, arg2, &downloaded, &total );" in download_info_block
    assert "clc.downloadCount" not in download_info_block
    assert "clc.downloadSize" not in download_info_block
