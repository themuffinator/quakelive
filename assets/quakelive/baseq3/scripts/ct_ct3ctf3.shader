//SKY
textures/ct_ct3ctf3/sky
{
	skyparms - 512 -

	q3map_lightImage textures/ct_ct3ctf3/env/sky_01.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	q3map_globaltexture
	q3map_lightsubdivide 256
	q3map_lightmapFilterRadius 0 8
	q3map_sunlight 100
	surfaceparm sky
	q3map_sun .8 .8 1 200 320 70
	skyparms - 512 -
	qer_editorimage textures/ct_ct3ctf3/env/sky_01.tga

	{
		map textures/ct_ct3ctf3/env/sky_01.tga
		tcMod scale 10 10
		tcMod scroll .05 .09
		depthWrite
	}


	{
		map textures/ct_ct3ctf3/env/sky_02.tga
		blendFunc filter
		tcMod scale 4 4
		tcMod scroll 0.01 0.01
	}
} 

textures/ct_ct3ctf3/glass
{
    qer_editorimage textures/ct_ct3ctf3/glass_2.tga
	surfaceparm nomarks
    surfaceparm trans
    cull disable
	q3map_surfacelight 50
	q3map_lightimage textures/ct_ct3ctf3/glass_2_blend.tga
	sort 7
	{
		map $lightmap
		rgbGen identity
	}
	{
        map textures/ct_ct3ctf3/glass_2.tga
        blendfunc blend
    }
	{
		map textures/ct_ct3ctf3/glass_2_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_ct3ctf3/glass_nolight
{
    qer_editorimage textures/ct_ct3ctf3/glass_2.tga
	surfaceparm nomarks
    surfaceparm trans
    cull disable
	sort 7
	{
		map $lightmap
		rgbGen identity
	}
	{
        map textures/ct_ct3ctf3/glass_2.tga
    }
	{
        map textures/ct_ct3ctf3/glass.tga
		blendfunc filter
    }
}

textures/ct_ct3ctf3/lamp_glass
{
	surfaceparm nomarks
	qer_editorimage textures/ct_ct3ctf3/lamp_glass.tga
	q3map_surfacelight 400
	q3map_lightsubdivide 8
	q3map_lightimage textures/ct_ct3ctf3/lamp_glass_blend.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3ctf3/lamp_glass.tga
		//blendFunc GL_DST_COLOR GL_ZERO
		blendFunc filter
		rgbGen identity
	}
	{
		map textures/ct_ct3ctf3/lamp_glass_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_ct3ctf3/red_lamp
{
	surfaceparm nomarks
	qer_editorimage textures/ct_ct3ctf3/red_lamp.tga
	q3map_surfacelight 300
	q3map_lightimage textures/ct_ct3ctf3/red_lamp_blend.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3ctf3/red_lamp.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3ctf3/red_lamp_blend.tga
		blendfunc add
	}
}

textures/ct_ct3ctf3/blue_lamp
{
	surfaceparm nomarks
	qer_editorimage textures/ct_ct3ctf3/blue_lamp.tga
	q3map_surfacelight 300
	q3map_lightimage textures/ct_ct3ctf3/blue_lamp_blend.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3ctf3/blue_lamp.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3ctf3/blue_lamp_blend.tga
		blendfunc add
	}
}

textures/ct_ct3ctf3/red_banner
{
        tessSize 64
        deformVertexes wave 194 sin 0 3 0 .4
        deformVertexes normal .3 .2
        surfaceparm nomarks
        cull none

    {
		map textures/ct_ct3ctf3/red_banner.tga
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
        //blendFunc GL_ONE GL_ONE            
        blendFunc GL_DST_COLOR GL_ZERO
        rgbGen identity
	}
}