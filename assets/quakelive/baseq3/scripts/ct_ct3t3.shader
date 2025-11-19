// ct_ct3t3 BY CITYY
// 1on1 DUEL MAP

// HIGH RES EXTERNAL LIGHTMAP
// BASE SHADER

textures/ct3tourney3/my_texture_hi_res_lightmap
{
  q3map_lightmapSize 1024 1024
  q3map_lightmapBrightness 2.0
}

// LAMPS
// BLUE 512*256

textures/ct_ct3t3/lamp_01
{
	surfaceparm nomarks
	qer_editorimage textures/ct_ct3t3/lamp_01.tga
	
	{

		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/lamp_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/lamp_01_blend1.tga
		blendfunc GL_ONE GL_ONE
	}
	{
		map textures/ct_ct3t3/lamp_01_blend2.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		rgbGen identity
	}
}

//BLUE 128*512

textures/ct_ct3t3/lamp_03
{
	surfaceparm nomarks
	qer_editorimage textures/ct_ct3t3/lamp_03.tga
	
	{

		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/lamp_03.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/lamp_03_blend1.tga
		blendfunc GL_ONE GL_ONE
	}
	{
		map textures/ct_ct3t3/lamp_03_blend2.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		rgbGen identity
	}
}

// BLUE 512*256 CRACKED

textures/ct_ct3t3/lamp_01_cracked
{
	surfaceparm nomarks
	qer_editorimage textures/ct_ct3t3/lamp_01_cracked.tga
	
	{

		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/lamp_01_cracked.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/lamp_01_blend1.tga
		blendfunc GL_ONE GL_ONE
		rgbGen wave square .5 .5 0 1
	}
	{
		map textures/ct_ct3t3/lamp_01_blend2.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		rgbGen identity
	}
}

// ITEM SPAWN
// ROCKET LAUNCHER 256*256

textures/ct_ct3t3/item_marker_rl
{
	surfaceparm nomarks
	nopicmip
	qer_editorimage textures/ct_ct3t3/blend_rl.tga
	
	{

		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01_blend1.tga
		blendfunc GL_ONE GL_ONE
	}
	{
		map textures/ct_ct3t3/blend_rl.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		rgbGen identity
	}
}

// GRENADE LAUNCHER 256*256

textures/ct_ct3t3/item_marker_gl
{
	surfaceparm nomarks
	nopicmip
	qer_editorimage textures/ct_ct3t3/blend_gl.tga
	
	{

		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01_blend1.tga
		blendfunc GL_ONE GL_ONE
	}
	{
		map textures/ct_ct3t3/blend_gl.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		rgbGen identity
	}
}

// LIGHTNING GUN 256*256

textures/ct_ct3t3/item_marker_lg
{
	surfaceparm nomarks
	nopicmip
	qer_editorimage textures/ct_ct3t3/blend_lg.tga
	
	{

		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01_blend1.tga
		blendfunc GL_ONE GL_ONE
	}
	{
		map textures/ct_ct3t3/blend_lg.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		rgbGen identity
	}
} 

// PLASMA GUN 256*256

textures/ct_ct3t3/item_marker_pg
{
	surfaceparm nomarks
	nopicmip
	qer_editorimage textures/ct_ct3t3/blend_pg.tga
	
	{

		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01_blend1.tga
		blendfunc GL_ONE GL_ONE
	}
	{
		map textures/ct_ct3t3/blend_pg.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		rgbGen identity
	}
} 

// SHOTGUN 256*256

textures/ct_ct3t3/item_marker_sg
{
	surfaceparm nomarks
	nopicmip
	qer_editorimage textures/ct_ct3t3/blend_sg.tga
	
	{

		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01_blend1.tga
		blendfunc GL_ONE GL_ONE
	}
	{
		map textures/ct_ct3t3/blend_sg.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		rgbGen identity
	}
} 

// ARMOR 256*256

textures/ct_ct3t3/item_marker_ya
{
	surfaceparm nomarks
	nopicmip
	qer_editorimage textures/ct_ct3t3/blend_ya.tga
	
	{

		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01_blend1.tga
		blendfunc GL_ONE GL_ONE
	}
	{
		map textures/ct_ct3t3/blend_ya.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		rgbGen identity
	}
} 

// UPARROW 256*256

textures/ct_ct3t3/item_marker_up
{
	surfaceparm nomarks
	nopicmip
	qer_editorimage textures/ct_ct3t3/blend_up.tga
	
	{

		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01_blend1.tga
		blendfunc GL_ONE GL_ONE
	}
	{
		map textures/ct_ct3t3/blend_up.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		rgbGen identity
	}
} 

// DOWNARROW 256*256

textures/ct_ct3t3/item_marker_down
{
	surfaceparm nomarks
	nopicmip
	qer_editorimage textures/ct_ct3t3/blend_down.tga
	
	{

		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01_blend1.tga
		blendfunc GL_ONE GL_ONE
	}
	{
		map textures/ct_ct3t3/blend_down.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		rgbGen identity
	}
} 

// LEFTARROW 256*256

textures/ct_ct3t3/item_marker_left
{
	surfaceparm nomarks
	nopicmip
	qer_editorimage textures/ct_ct3t3/blend_left.tga
	
	{

		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01_blend1.tga
		blendfunc GL_ONE GL_ONE
	}
	{
		map textures/ct_ct3t3/blend_left.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		rgbGen identity
	}
} 

// RIGHTARROW 256*256

textures/ct_ct3t3/item_marker_right
{
	surfaceparm nomarks
	nopicmip
	qer_editorimage textures/ct_ct3t3/blend_right.tga
	
	{

		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01_blend1.tga
		blendfunc GL_ONE GL_ONE
	}
	{
		map textures/ct_ct3t3/blend_right.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		rgbGen identity
	}
} 

// FLAG 256*256

textures/ct_ct3t3/item_marker_flag
{
	surfaceparm nomarks
	nopicmip
	qer_editorimage textures/ct_ct3t3/blend_flag.tga
	
	{
		
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01_blend1.tga
		blendfunc GL_ONE GL_ONE
	}
	{
		map textures/ct_ct3t3/blend_flag.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		rgbGen identity
	}
} 

// POWERUP 256*256

textures/ct_ct3t3/item_marker_pu
{
	surfaceparm nomarks
	nopicmip
	qer_editorimage textures/ct_ct3t3/blend_pu.tga
	
	{
		
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01_blend1.tga
		blendfunc GL_ONE GL_ONE
	}
	{
		map textures/ct_ct3t3/blend_pu.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		rgbGen identity
	}
} 

// MEGAHEALTH 256*256

textures/ct_ct3t3/item_marker_mh
{
	surfaceparm nomarks
	nopicmip
	qer_editorimage textures/ct_ct3t3/blend_mh.tga
	
	{
		
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01_blend1.tga
		blendfunc GL_ONE GL_ONE
	}
	{
		map textures/ct_ct3t3/blend_mh.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		rgbGen identity
	}
} 


// ITEM MARKER
// ROCKET LAUNCHER 256*256 CRACKED

textures/ct_ct3t3/item_marker_rl_cracked
{
	surfaceparm nomarks
	nopicmip
	qer_editorimage textures/ct_ct3t3/blend_RL.tga
	
	{
		
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01_cracked.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01_blend1.tga
		blendfunc GL_ONE GL_ONE
		rgbGen wave square .5 .5 0 1
	}
	{
		map textures/ct_ct3t3/blend_RL.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		rgbGen identity
	}
}

// FLAG CRACKED 256*256

textures/ct_ct3t3/item_marker_flag_cracked
{
	surfaceparm nomarks
	nopicmip
	qer_editorimage textures/ct_ct3t3/blend_flag.tga
	
	{
		
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01_cracked.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/item_marker_01_blend1.tga
		blendfunc GL_ONE GL_ONE
	}
	{
		map textures/ct_ct3t3/blend_flag.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		rgbGen identity
	}
} 

// JUMPPADS
// BLUE

textures/ct_ct3t3/jp_01_alpha_green
{
	surfaceparm nodamage
	qer_editorimage textures/ct_ct3t3/jp_01_alpha_green.tga
	
	{
		map textures/ct_ct3t3/jp_01_alpha_green.tga
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
	{
		map textures/ct_ct3t3/bouncepad01b_layer1_green.tga
		blendfunc add
		rgbGen wave sin .5 .5 0 1.5	
	}
	{
		clampmap textures/ct_ct3t3/jp_01_ring_green.tga
		blendfunc add
		tcMod stretch sin 1.2 .8 0 1.5
		rgbGen wave square .5 .5 .25 1.5
	}
}

// JUMPPAD WALL
// BLUE - 1024^2

textures/ct_ct3t3/jumppad_wall_blue
{
	qer_editorimage textures/ct_ct3t3/jumppad_wall_blue.tga
	q3map_surfacelight 60
	q3map_lightimage textures/ct_ct3ctf2/blue_tube.tga
	
	{
		map textures/ct_ct3t3/black.tga
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/jumppad_wall_blue_blend.tga
		blendfunc GL_ONE GL_ONE
		rgbGen identity
		//tcMod stretch sin 1 .01 0 1
		tcmod scroll 0 .25
	}
	{
		map textures/ct_ct3t3/jumppad_wall_blue.tga
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		
		map $lightmap
		rgbGen identity
		blendfunc GL_DST_COLOR GL_ZERO
	}	
}

//TERRAIN/ROCK

textures/ct_ct3t3/rock_01
{
	qer_editorimage textures/ct_ct3t3/rock_01.tga
	
	
	q3map_nonplanar
	q3map_shadeAngle 90
	
	{
		
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/rock_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

//SKY

textures/ct_ct3t3/sky
{
	qer_editorimage textures/ct_ct3t3/sky_blue.tga
	
	surfaceparm noimpact
	surfaceparm nolightmap
	q3map_globaltexture
	surfaceparm sky
	skyparms - 256 -
	
	q3map_sunExt 1 0.932311 0.77821 230 270 60 3 16
	q3map_lightmapFilterRadius 0 12		//self other
	q3map_skyLight 100 3
	
	nopicmip
	nomipmaps
	{
		map textures/ct_ct3t3/sky_blue.tga
		tcMod scale 8 8
		tcMod scroll .02 .02
		depthWrite
	}
	{
		map textures/ct_ct3t3/sky_clouds.tga
		blendFunc GL_ONE GL_ONE
		tcMod scale 4 4
		tcMod scroll 0.01 0.01
	}
} 

// METAL GRATE
// 512*256 with alpha channel

textures/ct_ct3t3/grate_01
{
    surfaceparm trans	
	surfaceparm alphashadow
   	surfaceparm nonsolid
	surfaceparm nomarks	
	cull none
    nopicmip
	
	{
		map textures/ct_ct3t3/grate_01.tga
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

// CONE PLASTIC
// 512*512 with alpha channel

textures/ct_ct3t3/cone_01
{
	
    surfaceparm trans	
	surfaceparm alphashadow
   	surfaceparm nonsolid
	surfaceparm nomarks	
	cull none
    nopicmip
	{
		map textures/ct_ct3t3/cone_01.tga
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

// MCSARGE'S
// 512*512

textures/ct_ct3t3/mcsarges
{
	qer_editorimage textures/ct_ct3t3/mcsarges.tga
	

	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	cull none
	nopicmip
	polygonOffset 	
	sort 6
	{
		map textures/ct_ct3t3/mcsarges.tga
		blendfunc add
	}
}

// MCSARGE'S 2
// 512*512

textures/ct_ct3t3/mcsarges2
{
	qer_editorimage textures/ct_ct3t3/mcsarges2.tga
	

	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	cull none
	nopicmip
	polygonOffset 	
	sort 6
	{
		map textures/ct_ct3t3/mcsarges2.tga
		blendfunc add
	}
}

// MANUFACTURING DECAL
// 512*256

textures/ct_ct3t3/manufacturing
{
	qer_editorimage textures/ct_ct3t3/manufacturing.tga
	

	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	cull none
	nopicmip
	polygonOffset 	
	sort 6
	{
		map textures/ct_ct3t3/manufacturing.tga
		blendfunc add
	}
}

// DEPOSIT&STOCK DECAL
// 512*256

textures/ct_ct3t3/depositstock
{
	qer_editorimage textures/ct_ct3t3/depositstock.tga
	

	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	cull none
	nopicmip
	polygonOffset 	
	sort 6
	{
		map textures/ct_ct3t3/depositstock.tga
		blendfunc add
	}
}

// LUCY's CANTEEN DECAL
// 512*256

textures/ct_ct3t3/lucyscanteen
{
	qer_editorimage textures/ct_ct3t3/lucyscanteen.tga
	

	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	cull none
	nopicmip
	polygonOffset 	
	sort 6
	{
		map textures/ct_ct3t3/lucyscanteen.tga
		blendfunc add
	}
}

// EMPLOYEE OF THE MONTH DECAL
// 256*128

textures/ct_ct3t3/employeeofthemonth
{
	qer_editorimage textures/ct_ct3t3/employeeofthemonth.tga
	

	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	cull none
	nopicmip
	polygonOffset 	
	sort 6
	{
		map textures/ct_ct3t3/employeeofthemonth.tga
		blendfunc add
	}
}

// SIGN_01
// 256*256 with alpha channel

textures/ct_ct3t3/sign_01
{
	
    surfaceparm trans	
	surfaceparm alphashadow
   	surfaceparm nonsolid
	surfaceparm nomarks	
	cull none
    nopicmip
	{
		map textures/ct_ct3t3/sign_01.tga
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

// SIGN_02
// 256*256 with alpha channel

textures/ct_ct3t3/sign_02
{
	
    surfaceparm trans	
	surfaceparm alphashadow
   	surfaceparm nonsolid
	surfaceparm nomarks	
	cull none
    nopicmip
	{
		map textures/ct_ct3t3/sign_02.tga
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

// SIGN_03
// 256*256 with alpha channel

textures/ct_ct3t3/sign_03
{
	
    surfaceparm trans	
	surfaceparm alphashadow
   	surfaceparm nonsolid
	surfaceparm nomarks	
	cull none
    nopicmip
	{
		map textures/ct_ct3t3/sign_03.tga
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

// SIGN_04
// 256*256 with alpha channel

textures/ct_ct3t3/sign_04
{
	
    surfaceparm trans	
	surfaceparm alphashadow
   	surfaceparm nonsolid
	surfaceparm nomarks	
	cull none
    nopicmip
	{
		map textures/ct_ct3t3/sign_04.tga
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

// SIGN_05
// 512*256 with alpha channel

textures/ct_ct3t3/sign_05
{
	
    surfaceparm trans	
	surfaceparm alphashadow
   	surfaceparm nonsolid
	surfaceparm nomarks	
	cull none
    nopicmip
	{
		map textures/ct_ct3t3/sign_05.tga
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

// SIGN_06
// 256*256 with alpha channel

textures/ct_ct3t3/sign_06
{
	
    surfaceparm trans	
	surfaceparm alphashadow
   	surfaceparm nonsolid
	surfaceparm nomarks	
	cull none
    nopicmip
	{
		map textures/ct_ct3t3/sign_06.tga
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

// SIGN_07
// 512*256 with alpha channel

textures/ct_ct3t3/sign_07
{
	
    surfaceparm trans	
	surfaceparm alphashadow
   	surfaceparm nonsolid
	surfaceparm nomarks	
	cull none
    nopicmip
	{
		map textures/ct_ct3t3/sign_07.tga
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

// SIGN_08
// 256*256 with alpha channel

textures/ct_ct3t3/sign_08
{
	
    surfaceparm trans	
	surfaceparm alphashadow
   	surfaceparm nonsolid
	surfaceparm nomarks	
	cull none
    nopicmip
	{
		map textures/ct_ct3t3/sign_08.tga
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

// SIGN_09
// 512*256 with alpha channel

textures/ct_ct3t3/sign_09
{
	
    surfaceparm trans	
	surfaceparm alphashadow
   	surfaceparm nonsolid
	surfaceparm nomarks	
	cull none
    nopicmip
	{
		map textures/ct_ct3t3/sign_09.tga
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

// SIGN_10
// 256*256 with alpha channel

textures/ct_ct3t3/sign_10
{
	
    surfaceparm trans	
	surfaceparm alphashadow
   	surfaceparm nonsolid
	surfaceparm nomarks	
	cull none
    nopicmip
	{
		map textures/ct_ct3t3/sign_10.tga
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

// SIGN_11
// 256*256 with alpha channel

textures/ct_ct3t3/sign_11
{
	
    surfaceparm trans	
	surfaceparm alphashadow
   	surfaceparm nonsolid
	surfaceparm nomarks	
	cull none
    nopicmip
	{
		map textures/ct_ct3t3/sign_11.tga
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

// SIGN_13
// 512*256 with alpha channel

textures/ct_ct3t3/sign_13
{
	
    surfaceparm trans	
	surfaceparm alphashadow
   	surfaceparm nonsolid
	surfaceparm nomarks	
	cull none
    nopicmip
	{
		map textures/ct_ct3t3/sign_13.tga
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

// Tools
// 256*128 with alpha channel

textures/ct_ct3t3/tools
{
	
    surfaceparm trans	
	surfaceparm alphashadow
   	surfaceparm nonsolid
	surfaceparm nomarks	
	cull none
    nopicmip
	{
		map textures/ct_ct3t3/tools.tga
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

// VENT_01
// 256*256 with alpha channel

textures/ct_ct3t3/vent_01
{
	
    surfaceparm trans	
	surfaceparm alphashadow
   	surfaceparm nonsolid
	surfaceparm nomarks	
	cull none
    nopicmip
	{
		map textures/ct_ct3t3/vent_01.tga
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

// VENT_03_alpha
// 512*512 with alpha channel

textures/ct_ct3t3/vent_03_alpha
{
	
    surfaceparm trans	
	surfaceparm alphashadow
   	surfaceparm nonsolid
	surfaceparm nomarks	
	qer_editorimage textures/ct_ct3t3/vent_03.tga
	cull none
    nopicmip
	{
		map textures/ct_ct3t3/vent_03.tga
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

// VENT_04
// 256*256 with alpha channel

textures/ct_ct3t3/vent_04
{
	
    surfaceparm trans	
	surfaceparm alphashadow
   	surfaceparm nonsolid
	surfaceparm nomarks	
	qer_editorimage textures/ct_ct3t3/vent_04.tga
	cull none
    nopicmip
	{
		map textures/ct_ct3t3/vent_04.tga
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

textures/ct_ct3t3/box_01
{
	
    surfaceparm trans	
	surfaceparm alphashadow
   	surfaceparm nonsolid
	surfaceparm nomarks	
	qer_editorimage textures/ct_ct3t3/box_01.tga
	cull none
    nopicmip
	polygonoffset
	sort 6
	{
		map textures/ct_ct3t3/box_01.tga
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

textures/ct_ct3t3/vent_05
{
	
    surfaceparm trans	
    surfaceparm nomarks	
	cull none
    nopicmip
	{
		clampmap textures/ct_ct3t3/vent_05.tga
		tcMod rotate 800
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

textures/ct_ct3t3/vent_05b
{
	
    qer_editorimage textures/ct_ct3t3/vent_05.tga
	surfaceparm trans	
    surfaceparm nomarks	
	cull none
    nopicmip
	{
		clampmap textures/ct_ct3t3/vent_05.tga
		tcMod rotate 1024
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

// BIRD_01
// 256*256 with alpha channel

textures/ct_ct3t3/bird_01
{
	
    surfaceparm trans	
	surfaceparm alphashadow
   	surfaceparm nonsolid
	surfaceparm nomarks	
	qer_editorimage textures/ct_ct3t3/bird_01.tga
	cull none
    nopicmip
	{
		map textures/ct_ct3t3/bird_01.tga
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


// CHAIN
// 256*512 with alpha channel

textures/ct_ct3t3/chain_01
{
	
     cull disable
     deformVertexes autoSprite2
     deformVertexes wave 100 sin 0 3 0 .05
     deformVertexes wave 100 sin 0 3 0 .3
    {
		map textures/ct_ct3t3/chain_01.tga
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

// GAUGES
// 512*512

textures/ct_ct3t3/gauge_01_360
{
	
	qer_editorimage textures/ct_ct3t3/gauge_01.tga
	surfaceparm nomarks
	{

		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/gauge_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		clampmap textures/ct_ct3t3/gauge_01_blend.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		tcmod rotate 80
	}
}

textures/ct_ct3t3/gauge_01_540
{
	
	qer_editorimage textures/ct_ct3t3/gauge_01.tga
	surfaceparm nomarks
	{

		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/gauge_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		clampmap textures/ct_ct3t3/gauge_01_blend.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		tcmod rotate 100
	}
}

// NONSOLID WOOD

//BRIGHT WOOD_03
textures/ct_ct3t3/wood_03_nonsolid
{
	
	qer_editorimage textures/ct_ct3t3/wood_03.tga
	surfaceparm nonsolid
	{

		map $lightmap
		rgbGen identity	
	}
	{
		map textures/ct_ct3t3/wood_03.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO	
	}
}

//DARK WOOD_03b
textures/ct_ct3t3/wood_03b_nonsolid
{
	
	qer_editorimage textures/ct_ct3t3/wood_03b.tga
	surfaceparm nonsolid
	{
		
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/wood_03b.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

//DARK WOOD_06
textures/ct_ct3t3/wood_06_nonsolid
{
	
	qer_editorimage textures/ct_ct3t3/wood_06.tga
	surfaceparm nonsolid
	{
		
		map $lightmap
		rgbGen identity	
	}
	{
		map textures/ct_ct3t3/wood_06.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO	
	}
}

//DARK PAINTED WOOD_06b
textures/ct_ct3t3/wood_06b_nonsolid
{
	
	qer_editorimage textures/ct_ct3t3/wood_06b.tga
	surfaceparm nonsolid
	{
		
		map $lightmap
		rgbGen identity	
	}
	{
		map textures/ct_ct3t3/wood_06b.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO	
	}
}

//NONSOLID SOIL
//MUD_01_NONSOLID

textures/ct_ct3t3/mud_01_nonsolid
{
	
	qer_editorimage textures/ct_ct3t3/mud_01.tga
	surfaceparm nonsolid
	{
		
		map $lightmap
		rgbGen identity
	
	}
	{
		map textures/ct_ct3t3/mud_01.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

//PLATES_01_NONSOLID

textures/ct_ct3t3/plates_01_nonsolid
{
	
	qer_editorimage textures/ct_ct3t3/plates_01.tga
	surfaceparm nonsolid
	{
		
		map $lightmap
		rgbGen identity
	
	}
	{
		map textures/ct_ct3t3/plates_01.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

//TRIM_03_NONSOLID

textures/ct_ct3t3/trim_03_nonsolid
{
	
	qer_editorimage textures/ct_ct3t3/trim_03.tga
	surfaceparm nonsolid
	{
		
		map $lightmap
		rgbGen identity
	
	}
	{
		map textures/ct_ct3t3/trim_03.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO	
	}
}

//TRIM_03b_NONSOLID

textures/ct_ct3t3/trim_03b_nonsolid
{
	
	qer_editorimage textures/ct_ct3t3/trim_03b.tga
	surfaceparm nonsolid
	{
		
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/trim_03b.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

// JUMPPAD 512*256 CRACKED

textures/ct_ct3t3/jp_01
{
	
	surfaceparm nomarks
	q3map_surfacelight 100
	q3map_lightimage textures/ct_ct3t3/jp_01_blend.tga
	qer_editorimage textures/ct_ct3t3/jp_01.tga
	{
		
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/jp_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3t3/jp_01_blend.tga
		blendFunc GL_ONE GL_ONE
		rgbGen wave sin .5 .5 0 5
	}
}

textures/ct_ct3t3/movesquare4
{
	
	qer_editorimage textures/ct_ct3t3/jumpring4.jpg
	qer_trans .5		
	surfaceparm noimpact
	surfaceparm nolightmap
	cull none
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nodlight
	deformvertexes move 0 0 10 sawtooth 0 1 .625 2
	sort 6
	{
		clampmap textures/ct_ct3t3/jumpring4.jpg
		rgbGen wave sawtooth 1 -1 .625 2
		blendfunc add
	}
}

textures/ct_ct3t3/proto_rustygrate
{
	
	surfaceparm	metalsteps	
    surfaceparm trans	
	surfaceparm alphashadow
	surfaceparm nonsolid
	cull none
    nopicmip
	{
		map textures/ct_ct3t3/proto_rustygrate.tga
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

//ADS

textures/ct_ct3t3/MassacreServers_512x512
{
      surfaceparm nomarks 
      qer_editorimage textures/ct_ct3t3/MassacreServers_512x512.tga 
      nopicmip 
   {
      map textures/ct_ct3t3/MassacreServers_512x512.tga 
   }
}

textures/ct_ct3t3/MaverickServers_512x512
{
      surfaceparm nomarks 
      qer_editorimage textures/ct_ct3t3/MaverickServers_512x512.tga 
      nopicmip 
   {
      map textures/ct_ct3t3/MaverickServers_512x512.tga 
   }
}

textures/ct_ct3t3/Sapphire_512x512
{
      surfaceparm nomarks 
      qer_editorimage textures/ct_ct3t3/Sapphire_512x512.tga 
      nopicmip 
   {
      map textures/ct_ct3t3/Sapphire_512x512.tga 
   }
}

textures/ct_ct3t3/Steel_Storm_512x512
{
      surfaceparm nomarks 
      qer_editorimage textures/ct_ct3t3/Steel_Storm_512x512.tga 
      nopicmip 
   {
      map textures/ct_ct3t3/Steel_Storm_512x512.tga 
   }
}

textures/ct_ct3t3/Wacom_512x512
{
      surfaceparm nomarks 
      qer_editorimage textures/ct_ct3t3/Wacom_512x512.tga 
      nopicmip 
   {
      map textures/ct_ct3t3/Wacom_512x512.tga 
   }
}

textures/ct_ct3t3/white
{
      surfaceparm nomarks 
      qer_editorimage textures/ct_ct3t3/white.tga 
      nopicmip 
   {
      map textures/ct_ct3t3/white.tga 
   }
}

//PROTOFENCE NONSOLID

textures/ct_ct3t3/proto_fence
{
	qer_editorimage textures/base_trim/proto_fence.tga
	surfaceparm trans		
	cull none
        nopicmip
		surfaceparm nonsolid
		surfaceparm nomarks

	{
		map textures/base_trim/proto_fence.tga
		tcMod scale 3 3
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