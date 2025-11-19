//TELEPORTER SHADER 

textures/ct_fuse/fuse_teleporter_beam
{
	qer_editorimage textures/ct_fuse/fuse_teleporter_beam.tga
	surfaceparm trans	
	surfaceparm nomarks	
	surfaceparm nonsolid
	surfaceparm nolightmap
	qer_trans .6
	cull none
	nopicmip
	{
		map textures/ct_fuse/fuse_teleporter_beam.tga
		blendfunc add
	} 
	{
		map textures/ct_fuse/fuse_teleporter_numbers_01.tga
		tcmod scroll 0 .6
		blendfunc add
	} 
	{
		map textures/ct_fuse/fuse_teleporter_numbers_02.tga
		tcmod scroll 0 1
		blendfunc add
	} 
}

//TELEPORTER SHADER (EASTEREGG)

textures/ct_fuse/fuse_teleporter_beam_easteregg
{
	qer_editorimage textures/ct_fuse/fuse_teleporter_beam.tga
	surfaceparm trans	
	surfaceparm nomarks	
	surfaceparm nonsolid
	surfaceparm nolightmap
	qer_trans .6
	cull none
	nopicmip
	{
		map textures/ct_fuse/fuse_teleporter_beam.tga
		blendfunc add
	} 
	{
		map textures/ct_fuse/fuse_teleporter_numbers_01.tga
		tcmod scroll 0 .6
		blendfunc add
	} 
	{
		map textures/ct_fuse/fuse_teleporter_numbers_02.tga
		tcmod scroll 0 1
		blendfunc add
	} 
	{
		map textures/ct_fuse/fuse_easteregg_blend.tga
		tcmod scroll 0 .5
		blendfunc add
	} 
}

// BIRD_01
// 256*256 with alpha channel

textures/ct_fuse/bird_01
{
    surfaceparm trans	
	surfaceparm alphashadow
   	surfaceparm nonsolid
	surfaceparm nomarks	
	qer_editorimage textures/ct_fuse/bird_01.tga
	cull none
    nopicmip
	{
		map textures/ct_fuse/bird_01.tga
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}
}