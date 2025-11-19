
textures/sgwdw/myfog
{
	qer_editorimage textures/sfx/fog_red.tga
	surfaceparm	trans
	surfaceparm	nonsolid
	surfaceparm	fog
	surfaceparm 	nodrop
	surfaceparm 	nolightmap
	q3map_globaltexture
	q3map_surfacelight 50
	fogparms ( .5 .2 .2 ) 350	//lower is more dense. 150 = med
	
	{
		map textures/liquids/kc_fogcloud3.tga
		blendfunc gl_dst_color gl_zero
		tcmod scale -.05 -.05
		tcmod scroll .01 -.01
		rgbgen identity
	}
}

textures/sgwdw/mysky
{
	qer_editorimage textures/skies/pjbasesky.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	q3map_globaltexture
	q3map_lightsubdivide 256 
	q3map_sun	0.266383 0.274632 0.358662 150 60 65
	q3map_surfacelight 200

	skyparms - 512 -
	
	{
		map textures/skies/dimclouds.tga
		tcMod scroll 0.01 0.01
		tcMod scale 3 3
		depthWrite
	}
	{
		map textures/skies/pjbasesky.tga
		blendfunc GL_ONE GL_ONE
		tcMod scroll -0.01 -0.01
		tcMod scale 5 5
	}
}

textures/sgwdw/mysky2
{
	qer_editorimage textures/tp_gothic/tp_stormclouds_001.tga
	q3map_lightimage textures/skies/pjbasesky_desaturated.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	q3map_globaltexture
	q3map_lightsubdivide 256 
	q3map_sunEx 0.35 0.35 0.35 160 60 65 3 16
	q3map_surfacelight 200
	skyparms - 512 -
	{
		map textures/tp_gothic/tp_stormclouds_001.tga
		tcMod scale 10 10
		tcMod scroll .05 .09
		depthWrite
	}
	{
		map textures/tp_gothic/tp_stormclouds_001.tga
		blendfunc add
		tcMod scale 4 4
		tcMod scroll 0.07 0.07
	}
}

textures/sgwdw/sg_light2_7k
{
	qer_editorimage textures/sgwdw/sg_light2.tga
	q3map_surfacelight 7000
	surfaceparm nomarks

	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/sgwdw/sg_light2.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/sgwdw/sg_light2-blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/sgwdw/sgwdw_redflag
{
        tessSize 64
        deformVertexes wave 194 sin 0 3 0 .4
        deformVertexes normal .3 .2
        surfaceparm nomarks
        surfaceparm nolightmap        
        cull none

	{
		map textures/sgwdw/sgwdw_redflag.tga
		rgbGen identity
	}

	{
		map textures/sgwdw/sgwdw_redflag.tga
	        blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen identity
	}

	{
       		map textures/sfx/shadow.tga
                tcGen environment 
                blendFunc GL_DST_COLOR GL_ZERO
       		rgbGen identity
	}
}



textures/sgwdw/sgwdw_blueflag
{
        tessSize 64
        deformVertexes wave 194 sin 0 3 0 .4
        deformVertexes normal .5 .1
        surfaceparm nomarks
        cull none
        
	{
		map textures/sgwdw/sgwdw_blueflag.tga
		rgbGen identity
	}

	{
		map textures/sgwdw/sgwdw_blueflag.tga
               	blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen identity
	}

	{
		map $lightmap
               	blendFunc GL_DST_COLOR GL_ONE_MINUS_DST_ALPHA
		rgbGen identity
	}

	{
       		map textures/sfx/shadow.tga
                tcGen environment 
                blendFunc GL_DST_COLOR GL_ZERO
       		rgbGen identity
	}
}


textures/sgwdw/sgwdw_clear_ripple3
{
	qer_editorimage textures/sgwdw/pool3d_3c.tga
	qer_trans .5
	q3map_globaltexture
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm water
	
	cull disable
	deformVertexes wave 64 sin .5 .5 0 .5	
		
	{ 
		map textures/sgwdw/pool3d_5c.tga
		blendFunc GL_dst_color GL_one
		rgbgen identity
		tcmod scale .5 .5
		tcmod transform 1.5 0 1.5 1 1 2
		tcmod scroll -.05 .001
	}
	
	{ 
		map textures/sgwdw/pool3d_6c.tga
		blendFunc GL_dst_color GL_one
		rgbgen identity
		tcmod scale .5 .5
		tcmod transform 0 1.5 1 1.5 2 1
		tcmod scroll .025 -.001
	}

	{ 
		map textures/sgwdw/pool3d_3c.tga
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




//portal
//Changed portal distance
textures/sgwdw/sgwdw_portal_sfx
{
	portal
	surfaceparm nolightmap


	{
	
		map textures/common/mirror1.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		depthWrite
	}

 
	{
		map textures/common/mirror1.tga
		blendfunc gl_src_alpha gl_one_minus_src_alpha
		depthFunc equal
		alphagen portal 4096
		rgbGen identityLighting	
	}
}








