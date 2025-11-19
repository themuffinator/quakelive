textures/sgtghost/Thx
{
	qer_editorimage textures/sgtghost/thx.tga
	q3map_lightimage textures/sgtghost/thx.tga
	q3map_surfacelight 100

	{
		animMap .15 textures/sgtghost/thx.tga textures/sgtghost/thx_1.tga textures/sgtghost/thx_2.tga textures/sgtghost/thx_3.tga textures/sgtghost/thx_4.tga
		rgbGen wave sawtooth 0 1 0 .15
	}
	{
		map textures/base_wall/comp3textb.tga
		blendfunc add
		rgbGen wave inversesawtooth 0 1 0 .15
		tcmod scroll 5 .25
	}
	{
		map textures/base_wall/comp3text.tga
		blendfunc add
		rgbGen identity
		tcmod scroll 2 2
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc gl_dst_color gl_zero
	}
	{
		map $lightmap
		tcgen environment
		tcmod scale .5 .5
		rgbGen wave sin .25 0 0 0
		blendfunc add
	}
}

textures/sgtghost/multiarena11
{
	qer_editorimage textures/sgtghost/Multiarena11.tga
	q3map_lightimage textures/sgtghost/Multiarena11.tga
	q3map_surfacelight 100

	{
		animMap .15 textures/sgtghost/Multiarena11.tga textures/sgtghost/Mahq_1.tga textures/sgtghost/Mahq_2.tga
		rgbGen wave sawtooth 0 1 0 .15
	}
	{
		map textures/base_wall/comp3textb.tga
		blendfunc add
		rgbGen wave inversesawtooth 0 1 0 .15
		tcmod scroll 5 .25
	}
	{
		map textures/base_wall/comp3text.tga
		blendfunc add
		rgbGen identity
		tcmod scroll 2 2
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc gl_dst_color gl_zero
	}
	{
		map $lightmap
		tcgen environment
		tcmod scale .5 .5
		rgbGen wave sin .25 0 0 0
		blendfunc add
	}
}

textures/sgtghost/sg_light
{
	qer_editorimage textures/sgtghost/sg_light.tga
	q3map_surfacelight 5000
	surfaceparm nomarks

	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/sgtghost/sg_light.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/sgtghost/sg_light-blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/sgtghost/sg_light2
{
	qer_editorimage textures/sgtghost/sg_light2.tga
	q3map_surfacelight 3000
	surfaceparm nomarks

	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/sgtghost/sg_light2.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/sgtghost/sg_light2-blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/sgtghost/sg_light2_7k
{
	qer_editorimage textures/sgtghost/sg_light2.tga
	q3map_surfacelight 7000
	surfaceparm nomarks

	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/sgtghost/sg_light2.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/sgtghost/sg_light2-blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/sgtghost/sg_lightYel
{
	qer_editorimage textures/sgtghost/sg_lightYel.tga
	q3map_surfacelight 7000
	surfaceparm nomarks

	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/sgtghost/sg_lightYel.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/sgtghost/sg_lightYel-blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/sgtghost/sg_light_1k
{
	qer_editorimage textures/sgtghost/sg_light.tga
	q3map_surfacelight 1000
	surfaceparm nomarks

	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/sgtghost/sg_light.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/sgtghost/sg_light-blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/sgtghost/sg_light_3k
{
	qer_editorimage textures/sgtghost/sg_light.tga
	q3map_surfacelight 3000
	surfaceparm nomarks

	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/sgtghost/sg_light.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/sgtghost/sg_light-blend.tga
		blendfunc GL_ONE GL_ONE
	}
}


textures/sgtghost/sgchromatic_portal
{
	qer_editorimage textures/sgtghost/sgchromatic_portal.tga
	q3map_lightimage textures/sgtghost/sgchromatic_portal.tga
	q3map_surfacelight 100

	{
		animMap .15 textures/sgtghost/sgchromatic_portal.tga textures/sgtghost/ghost.tga
		rgbGen wave sawtooth 0 1 0 .15
	}
	{
		map textures/base_wall/comp3textb.tga
		blendfunc add
		rgbGen wave inversesawtooth 0 1 0 .15
		tcmod scroll 5 .25
	}
	{
		map textures/base_wall/comp3text.tga
		blendfunc add
		rgbGen identity
		tcmod scroll 2 2
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc gl_dst_color gl_zero
	}
	{
		map $lightmap
		tcgen environment
		tcmod scale .5 .5
		rgbGen wave sin .25 0 0 0
		blendfunc add
	}
}

textures/sgtghost/sgrailing_portal
{
	qer_editorimage textures/sgtghost/sgrailing_portal.tga
	q3map_lightimage textures/sgtghost/sgrailing_portal.tga
	q3map_surfacelight 100

	{
		animMap .15 textures/sgtghost/sgrailing_portal.tga textures/sgtghost/ghost.tga
		rgbGen wave sawtooth 0 1 0 .15
	}
	{
		map textures/base_wall/comp3textb.tga
		blendfunc add
		rgbGen wave inversesawtooth 0 1 0 .15
		tcmod scroll 5 .25
	}
	{
		map textures/base_wall/comp3text.tga
		blendfunc add
		rgbGen identity
		tcmod scroll 2 2
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc gl_dst_color gl_zero
	}
	{
		map $lightmap
		tcgen environment
		tcmod scale .5 .5
		rgbGen wave sin .25 0 0 0
		blendfunc add
	}
}

textures/sgtghost/sgstadium_portal
{
	qer_editorimage textures/sgtghost/sgstadium_portal.tga
	q3map_lightimage textures/sgtghost/sgstadium_portal.tga
	q3map_surfacelight 100

	{
		animMap .15 textures/sgtghost/sgstadium_portal.tga textures/sgtghost/ghost.tga
		rgbGen wave sawtooth 0 1 0 .15
	}
	{
		map textures/base_wall/comp3textb.tga
		blendfunc add
		rgbGen wave inversesawtooth 0 1 0 .15
		tcmod scroll 5 .25
	}
	{
		map textures/base_wall/comp3text.tga
		blendfunc add
		rgbGen identity
		tcmod scroll 2 2
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc gl_dst_color gl_zero
	}
	{
		map $lightmap
		tcgen environment
		tcmod scale .5 .5
		rgbGen wave sin .25 0 0 0
		blendfunc add
	}
}

textures/sgtghost/sgtaho_portal
{
	qer_editorimage textures/sgtghost/sgaho_portal.tga
	q3map_lightimage textures/sgtghost/sgaho_portal.tga
	q3map_surfacelight 100

	{
		animMap .15 textures/sgtghost/sgaho_portal.tga textures/sgtghost/ghost.tga
		rgbGen wave sawtooth 0 1 0 .15
	}
	{
		map textures/base_wall/comp3textb.tga
		blendfunc add
		rgbGen wave inversesawtooth 0 1 0 .15
		tcmod scroll 5 .25
	}
	{
		map textures/base_wall/comp3text.tga
		blendfunc add
		rgbGen identity
		tcmod scroll 2 2
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc gl_dst_color gl_zero
	}
	{
		map $lightmap
		tcgen environment
		tcmod scale .5 .5
		rgbGen wave sin .25 0 0 0
		blendfunc add
	}
}

textures/sgtghost/sgtryout_portal
{
	qer_editorimage textures/sgtghost/sgtryout_portal.tga
	q3map_lightimage textures/sgtghost/sgtryout_portal.tga
	q3map_surfacelight 100

	{
		animMap .15 textures/sgtghost/sgtryout_portal.tga textures/sgtghost/ghost.tga
		rgbGen wave sawtooth 0 1 0 .15
	}
	{
		map textures/base_wall/comp3textb.tga
		blendfunc add
		rgbGen wave inversesawtooth 0 1 0 .15
		tcmod scroll 5 .25
	}
	{
		map textures/base_wall/comp3text.tga
		blendfunc add
		rgbGen identity
		tcmod scroll 2 2
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc gl_dst_color gl_zero
	}
	{
		map $lightmap
		tcgen environment
		tcmod scale .5 .5
		rgbGen wave sin .25 0 0 0
		blendfunc add
	}
}



textures/sgtghost/sg_metfloor
{
	qer_editorimage textures/sgtghost/sg_metfloor.tga
	surfaceparm metalsteps

	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/sgtghost/sg_metfloor.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbgen identity
	}
}



textures/sgtghost/red1
{
	surfaceparm nolightmap
	surfaceparm nonsolid
	cull twosided
	{
		map textures/sgtghost/red1.tga
		tcGen environment
                tcMod turb 0 0.25 0 0.5
                tcmod scroll 1 1
		blendfunc GL_ONE GL_ONE
	}
}



textures/sgtghost/sgroof
{
	qer_editorimage textures/sgtghost/sgroof.tga
	surfaceparm slick

	{
		map $lightmap
		rgbGen identity
	}

	{
		map textures/sgtghost/sgroof.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbgen identity
	}
}


textures/sgtghost/DS_ra3banner
{
     cull disable
     surfaceparm alphashadow
     surfaceparm trans	
     surfaceparm nomarks
     tessSize 64
     deformVertexes wave 30 sin 0 3 0 .2
     deformVertexes wave 100 sin 0 3 0 .7
     
        {
                map textures/sgtghost/DS_ra3banner.tga
                alphaFunc GE128
		depthWrite
		rgbGen vertex
        }
        {
		map $lightmap
		rgbGen identity
		blendFunc filter
		depthFunc equal
	}


}




