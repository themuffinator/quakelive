// ************************************************************************
// ** Chickenmap #2 Shader file						 **
// ** Midnight Keep by Geit (ouwegeit@goat.gamepoint.net)		 **
// ** (http://goat.gamepoint.net/)					 **
// **									 **
// ** Visit the chickenteam site at:					 **
// ** http://www.chickenteam.org					 **
// **									 **
// ** All shaders not by Sock, Natestah or Grim Reaper have been made	 **
// ** by Geit. Either alterations of other textures/shaders or made from **
// ** scratch								 **
// **									 **
// ** Geit - http://goat.gamepoint.net/					 **
// ** Sock - http://www.planetquake.com/simland/			 **
// ************************************************************************
//
// Shader Index:
// models/mapobjects/GR_trees/tree3			- Grim Reaper
// models/mapobjects/nateleaf1/tree2			- Natestah
// textures/geit/arch_gold				- Geit/Sock
// textures/geit/ct_bluedm				- Geit
// textures/geit/ct_reddm				- Geit
// textures/geit/ct_combodm				- Geit
// textures/geit/geit3ctf2_foam				- Geit
// textures/geit/geit3ctf2_omnipresentfog		- Geit
// textures/geit/geit3ctf2_waterval			- Unknown Author
// textures/geit/grave_skybox				- Sock
// textures/geit/graysky				- Geit
// textures/geit/pjwal2k_trans				- Geit
// textures/geit/zplants1				- Geit/Sock
// textures/gothic_xtra/center2trn_3b3dim		- Sock
// textures/medieval/flr_marble3_c3trn			- Sock
// textures/medieval/flr_marble3_c3trn_jp		- Sock
// textures/medieval/flr_marble5_c2trn			- Sock
// textures/medieval/flr_marble5_c3trn			- Sock
// textures/medieval/flr_marble5_c3trn_jp		- Sock


// The blue'ish fog that enshrouds the entire map	-	By Geit (modification of id shader)
// Taken out of the map, can't be arsed to remove this shader.. Can be arsed to add this line though.. O_o
textures/geit/geit3ctf2_omnipresentfog
{
	qer_editorimage textures/sfx/hellfog.tga
	qer_trans 0.4
	surfaceparm nonsolid
	surfaceparm nolightmap
	surfaceparm trans
	surfaceparm fog
	fogparms ( .04 .11 .21 ) 1024
}

// The sky overheard	-	By Geit (modification of id shader)
textures/geit/graysky
{
	qer_editorimage textures/skies/dimclouds.tga
	surfaceparm noimpact
	surfaceparm nomarks
	surfaceparm nolightmap
	q3map_sun 0.45 0.45 1 65 200 75
	q3map_surfacelight 40
	skyparms - 512 -

	{
		map textures/skies/dimclouds.tga
		tcMod scroll 0.005 0
		tcMod scale 2 2
		depthWrite
	}
}

// untranslucent gold window	-	Grate texture by Sock,	Golden window texture by Geit
textures/geit/arch_gold
{
	qer_editorimage textures/geit/arch_gold.tga
	surfaceparm nomarks
	q3map_surfacelight 800
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/geit/arch_gold.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/geit/arch_gold_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

// Transparant version of the bone thingy (So players cannot get stuck). Shader by Geit
textures/geit/pjwal2k_trans
{
	qer_editorimage textures/skin/pjwal2k.tga
	surfaceparm nonsolid
	{
		map $lightmap
		rgbGen identity
	
	}
	{
		map textures/skin/pjwal2k.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO

	
	}
}

// Texture by Sock, shader by Geit
textures/geit/zplants1
{
	qer_editorimage textures/medieval/zplants1.tga
	surfaceparm nonsolid
	{
		map $lightmap
		rgbGen identity
	
	}
	{
		map textures/medieval/zplants1.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO

	
	}
}

// Foam shader under the waterfalls. Shader by Geit
textures/geit/geit3ctf2_foam
	{
		qer_editorimage textures/liquids/pool3d_3.tga
		qer_trans .5
		q3map_globaltexture
		surfaceparm trans
		surfaceparm nonsolid
		surfaceparm water

		cull disable
		tessSize 8
		deformVertexes wave 8 sin 0 4 0 2
	
		
		{ 
			map textures/liquids/pool3d_5.tga
			blendFunc GL_dst_color GL_one
			rgbgen identity
			tcmod scale .5 .5
			tcmod transform 1.5 0 1.5 1 1 2
			tcmod scroll -.05 .001
		}
	
		{ 
			map textures/liquids/pool3d_6.tga
			blendFunc GL_dst_color GL_one
			rgbgen identity
			tcmod scale .5 .5
			tcmod transform 0 1.5 1 1.5 2 1
			tcmod scroll .025 -.001
		}

		{ 
			map textures/liquids/pool3d_3.tga
			blendFunc GL_dst_color GL_one
			rgbgen identity
			tcmod scale .25 .5
			tcmod scroll .001 .025
		}	

		{
			map $lightmap
			blendFunc GL_dst_color GL_zero
			rgbgen identity		
		}
}

// Red direction marker decal. By Geit
textures/geit/ct_reddm
{    
	qer_editorimage textures/geit/ct_reddm.tga
	surfaceparm nomarks 
	surfaceparm trans  
	surfaceparm pointlight
        
	{
		map textures/geit/ct_reddm.tga
                blendFunc add
		rgbGen vertex
	}
}

// Blue direction marker decal. By Geit
textures/geit/ct_bluedm
{    
	qer_editorimage textures/geit/ct_bluedm.tga
	surfaceparm nomarks 
	surfaceparm trans  
	surfaceparm pointlight
        
	{
		map textures/geit/ct_bluedm.tga
                blendFunc add
		rgbGen vertex
	}
}

// Blue direction marker decal. By Geit
textures/geit/ct_combodm
{    
	qer_editorimage textures/geit/ct_combodm.tga
	surfaceparm nomarks 
	surfaceparm trans  
	surfaceparm pointlight
        
	{
		map textures/geit/ct_combodm.tga
                blendFunc add
		rgbGen vertex
	}
}