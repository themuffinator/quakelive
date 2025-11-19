// ************************************************************************
// ** Geit3dm7 Shader File						 **
// ** The Olden Domain by Geit (ouwegeit@goat.gamepoint.net)		 **
// ** (http://goat.gamepoint.net/)					 **
// **									 **
// ** All shaders not by Sock or Todd Gantzler are made by Geit.	 **
// ** Either alterations of existing textures/shaders or made from 	 **
// ** scratch.								 **
// **									 **
// ** Geit - http://goat.gamepoint.net/					 **
// ** Sock - http://www.planetquake.com/simland				 **
// ************************************************************************
//
// Shader Index:
// models/mapobjects/multiplant/palmfrond		- Todd Gantzler
// models/mapobjects/multiplant/pleaf1			- Todd Gantzler
// models/mapobjects/multiplant/pleaf2			- Todd Gantzler
// models/mapobjects/multiplant/pleaf3			- Todd Gantzler
// models/mapobjects/palm2/trunk			- Todd Gantzler
// textures/geit/geit3dm8_desert_dust			- Geit
// textures/geit/lighttrick_yellow_100			- Geit
// textures/geit/dustball_skybox			- Sock
// textures/geit/geit_tele1				- Geit
// textures/egyptsoc_sfx/lig_064-01y2-2k		- Sock
// textures/egyptsoc_sfx/lig_064-02b1-2k		- Sock
// textures/egyptsoc_sfx/lig_064-02y2-2k		- Sock
// textures/egyptsoc_sfx/lig_064-04b1-2k		- Sock
// textures/egyptsoc_sfx/lig_064-05y2-2k		- Sock
// textures/egyptsoc_sfx/lig_v192-01wa			- Sock
// textures/egyptsoc_sfx/lig_v192-01yb			- Sock
// textures/egyptsoc_sfx/s128-01wc			- Sock
// textures/egyptsoc_sfx/s128-01we			- Sock
// textures/egyptsoc_sfx/wmblue_floor1a			- Sock
// textures/egyptsoc_sfx/wmblue_floor1b			- Sock
// textures/geit/geit3dm8_silentsand			- Geit

textures/geit/geit3dm8_desert_dust
{
	qer_editorimage textures/sfx/hellfog.tga
	qer_trans 0.4
	surfaceparm nonsolid
	surfaceparm nolightmap
	surfaceparm trans
	surfaceparm fog
	fogparms ( .86 .60 .23 ) 1024
}

textures/geit/lighttrick_yellow_100
{
	qer_editorimage textures/geit/g_egypt_light_3.tga
	q3map_lightimage textures/geit/g_egypt_light_3.tga

	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nonsolid
	surfaceparm noimpact
	surfaceparm nolightmap
	q3map_surfacelight 75

	skyparms - - -
	light 1
}

textures/geit/geit_tele1
{
	qer_editorimage textures/geit/geit_tele1.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm nomarks
	cull disable
	tessSize 128
	q3map_surfacelight 75
	{
		map textures/effects/envmap.tga
		rgbGen identity
		tcGen environment
	}
	{
		map textures/geit/geit_tele1.tga
		blendfunc blend
		rgbGen identity
		tcMod turb 0 0.3 0 0.2
	}
//	{
//		map textures/geit/geit_tele2.tga
//		tcGen environment
//              tcMod turb 0 0.25 0 0.5
//              tcmod scroll 1 1
//		blendfunc GL_ONE GL_ONE
//	}
	{
		map textures/effects/tinfx3.tga
		blendFunc GL_ONE GL_ONE
		tcGen environment
	}
}

textures/geit/geit3dm8_silentsand
{
	qer_editorimage textures/egyptsoc_mat/sand1b.tga
	surfaceparm nosteps		
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/egyptsoc_mat/sand1b.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}