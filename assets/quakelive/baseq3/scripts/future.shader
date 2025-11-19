/// Future Crossings Shader ///
/////////////////////////////////////////////////////////////////////
// I'd like to thank Ydnar for his textures (www.shaderlab.com)
// All Shaderlab content copyright © 2001 Randy Reddig.
/////////////////////////////////////////////////////////////////////

// non trans id rust shin
textures/future/s_deeprust
{
	qer_editorimage textures/base_trim/deeprust.tga
	surfaceparm nonsolid
	{
		map $lightmap
		rgbGen identity
	
	}
	{
		map textures/base_trim/deeprust.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO

	
	}
}
textures/future/s_otin
{   
   
        {
                map textures/future/s_otinfx.tga       
                tcGen environment
                rgbGen vertex
	}  
        {
		map textures/future/s_otin.tga
                blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen identity
	}
        {
		map $lightmap
                blendFunc GL_DST_COLOR GL_ONE_MINUS_DST_ALPHA
		rgbGen identity
	}
         
}
// evil 7 light
textures/future/e7slight
{
	qer_editorimage textures/future/e7slight.tga
	q3map_surfacelight 2000
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/future/e7slight.tga
	blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/future/e7slight_blend.tga
		rgbGen wave sin .6 .1 .1 .1
		blendfunc GL_ONE GL_ONE
	}
}

// evil 7 light
textures/future/e7trimlight
{
	qer_editorimage textures/future/e7trimlight.tga
	q3map_surfacelight 2000
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/future/e7trimlight.tga
	blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/future/e7trimlight_blend.tga
		rgbGen wave sin .6 .1 .1 .1
		blendfunc GL_ONE GL_ONE
	}
}
// evil railing
textures/future/e_mtlrail
{
	qer_editorimage textures/future/e_mtlrail.tga
    	surfaceparm trans	
	surfaceparm alphashadow
	surfaceparm playerclip
   	surfaceparm nonsolid
	surfaceparm nomarks	
	cull none
        nopicmip
	{
		map textures/future/e_mtlrail.tga
		tcMod scale 2 2
		blendFunc gl_one gl_zero
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc gl_dst_color gl_zero
		depthFunc equal
	}
}
textures/future/hh2_big_w_girder04
{
	qer_editorimage textures/future/hh2_big_w_girder04.tga
	surfaceparm trans
	surfaceparm nonsolid
	cull none
	{
		map textures/future/hh2_big_w_girder04.tga
		tcMod scale 2 2
		blendFunc gl_one gl_zero
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc gl_dst_color gl_zero
		depthFunc equal
	}
}
textures/future/hh2_big_w_girder01
{
	qer_editorimage textures/future/hh2_big_w_girder01.tga
	surfaceparm trans
	surfaceparm nonsolid
	cull none
	{
		map textures/future/hh2_big_w_girder01.tga
		tcMod scale 2 2
		blendFunc gl_one gl_zero
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc gl_dst_color gl_zero
		depthFunc equal
	}
}

// id flare from colua0 model
textures/future/scan_flare
{
	qer_editorimage textures/future/id_flare.tga	
	deformVertexes autoSprite

//	q3map_surfacelight	1000

	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nolightmap
	cull none	
	{
		Map textures/future/id_flare.tga
		blendFunc GL_ONE GL_ONE
	}	
	
}

// id sfx tesla no light
textures/future/id_teslacoil
{
	cull none
	q3map_lightimage textures/sfx/tesla1.tga	
	qer_editorimage textures/sfx/tesla1.tga
	{
		map $lightmap
		tcgen environment
		blendfunc filter
	}
	
	{
		map textures/sfx/tesla1.tga
		blendfunc add
		rgbgen wave sawtooth 0 1 0 5
		tcmod scale 1 .5
		tcmod turb 0 .1 0 1
		tcMod scroll -1 -1
	}
 
	
	
	{
		map textures/sfx/electricslime.tga
		blendfunc add
		rgbgen wave sin 0 .5 0 1
		tcmod scale .5 .5
		tcmod turb 0 .1 0 1
		tcmod rotate 180
		tcmod scroll -1 -1
	}

	{
		map textures/sfx/cabletest2.tga
		blendfunc blend
	}

}
textures/scanctf/id_border11c_red
{
	q3map_surfacelight 300
	qer_editorimage textures/base_trim/border11c.tga
	
	{
		map textures/base_trim/border11c.tga
		rgbGen identity
	}
	
	{
		map $lightmap
		rgbGen identity
		blendfunc gl_dst_color gl_zero
	}

	{
		map textures/base_trim/border11c_light.tga
		blendfunc gl_one gl_one
		rgbgen wave sin 1 .1 0 5
	}


	{
		map textures/future/border11c_pulse1b_red.tga
		blendfunc gl_one gl_one
		tcmod scale .035 1
		tcmod scroll -0.65 0


	}

	
}
