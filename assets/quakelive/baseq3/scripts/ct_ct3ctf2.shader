//JUMPPAD

textures/ct_ct3ctf2/jp_01
{
	surfaceparm nodamage
	qer_editorimage textures/ct_ct3ctf2/jp_01.tga
	{
		map textures/ct_ct3ctf2/jp_01.tga
		//rgbGen identity
	}
	
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
	}
	
	{
		map textures/ct_ct3ctf2/bouncepad01b_layer1_teal.tga
		blendfunc add
		rgbGen wave sin .5 .5 0 1.5	
	}

	{
		clampmap textures/ct_ct3ctf2/jp_01_ring.tga
		blendfunc add
		tcMod stretch sin 1.2 .8 0 1.5
		rgbGen wave square .5 .5 .25 1.5
	}
}

textures/ct_ct3ctf2/jp_01_alpha
{
	surfaceparm nodamage
	qer_editorimage textures/ct_ct3ctf2/jp_01_alpha.tga
	{
		map textures/ct_ct3ctf2/jp_01_alpha.tga
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
		map textures/ct_ct3ctf2/bouncepad01b_layer1_teal.tga
		blendfunc add
		rgbGen wave sin .5 .5 0 1.5	
	}

	{
		clampmap textures/ct_ct3ctf2/jp_01_ring.tga
		blendfunc add
		tcMod stretch sin 1.2 .8 0 1.5
		rgbGen wave square .5 .5 .25 1.5
	}
}

textures/ct_ct3ctf2/jp_01_red
{
	surfaceparm nodamage
	qer_editorimage textures/ct_ct3ctf2/jp_01.tga
	{
		map textures/ct_ct3ctf2/jp_01.tga
		rgbGen identity
	}
	
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
	}
	
	{
		map textures/ct_ct3ctf2/bouncepad01r_layer1_teal.tga
		blendfunc add
		rgbGen wave sin .5 .5 0 1.5	
	}

	{
		clampmap textures/ct_ct3ctf2/jp_01_ring_red.tga
		blendfunc add
		tcMod stretch sin 1.2 .8 0 1.5
		rgbGen wave square .5 .5 .25 1.5
	}
}

textures/ct_ct3ctf2/jp_01_red_alpha
{
	surfaceparm nodamage
	qer_editorimage textures/ct_ct3ctf2/jp_01_alpha.tga
	{
		map textures/ct_ct3ctf2/jp_01_alpha.tga
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
		map textures/ct_ct3ctf2/bouncepad01r_layer1_teal.tga
		blendfunc add
		rgbGen wave sin .5 .5 0 1.5	
	}

	{
		clampmap textures/ct_ct3ctf2/jp_01_ring_red.tga
		blendfunc add
		tcMod stretch sin 1.2 .8 0 1.5
		rgbGen wave square .5 .5 .25 1.5
	}
}

//SKYBOX

textures/ct_ct3ctf2/sky
{
	qer_editorimage textures/ct_ct3ctf2/env/sky.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	q3map_globaltexture
	q3map_lightsubdivide 256
	q3map_surfacelight 100
	surfaceparm sky
	q3map_sun 1 .9 .9 70 320 70
	skyparms - 256 -

	{
		map textures/ct_ct3ctf2/env/sky.tga
		tcMod scroll 0.005 0.005
		tcMod scale 4 4
		depthWrite
	}
}

textures/ct_ct3ctf2/sky_dark
{
	qer_editorimage textures/ct_ct3ctf2/env/sky_dark.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	q3map_globaltexture
	q3map_lightsubdivide 256
	q3map_surfacelight 100
	surfaceparm sky
	q3map_sun .8 .8 1 70 320 70
	skyparms - 256 -
	{
		map textures/ct_ct3ctf2/env/sky_dark.tga
		tcMod scroll 0.005 0.005
		tcMod scale 4 4
		depthWrite
	}
}

textures/ct_ct3ctf2/sky_dark_2
{
	qer_editorimage textures/ct_ct3ctf2/env/sky_dark.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	q3map_globaltexture
	q3map_lightsubdivide 256
	q3map_surfacelight 100
	surfaceparm sky
	q3map_sun .8 .8 1 70 320 70
	skyparms - 256 -
	{
		map textures/ct_ct3ctf2/env/sky_dark_2.tga
		tcMod scale 10 10
		tcMod scroll .05 .09
		depthWrite
	}


	{
		map textures/ct_ct3ctf2/env/sky_dark.tga
		blendFunc GL_ONE GL_ONE
		tcMod scale 4 4
		tcMod scroll 0.01 0.01
	}
} 

//LIGHTS

textures/ct_ct3ctf2/baslt4_nolight
{
	qer_editorimage textures/base_light/baslt4_1.tga
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/base_light/baslt4_1.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/base_light/baslt4_1.blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_ct3ctf2/yellow_light
{
	surfaceparm nomarks
	qer_editorimage textures/ct_ct3ctf2/lamp_01_yellow.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3ctf2/lamp_01_yellow.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3ctf2/lamp_01_yellow_blend.tga
		blendfunc GL_ONE GL_ONE
	}
	{
        map textures/ct_ct3ctf2/tinfx.tga       
        blendFunc add
		tcGen environment
        rgbGen identity
	}  
}

textures/ct_ct3ctf2/red_light
{
	surfaceparm nomarks
	qer_editorimage textures/ct_ct3ctf2/lamp_01_red.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3ctf2/lamp_01_red.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3ctf2/lamp_01_red_blend.tga
		blendfunc GL_ONE GL_ONE
	}
	{
        map textures/ct_ct3ctf2/tinfx.tga       
        blendFunc add
		tcGen environment
        rgbGen identity
	}  
}

textures/ct_ct3ctf2/blue_light
{
	surfaceparm nomarks
	qer_editorimage textures/ct_ct3ctf2/lamp_01_blue.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3ctf2/lamp_01_blue.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3ctf2/lamp_01_blue_blend.tga
		blendfunc GL_ONE GL_ONE
	}
	{
        map textures/ct_ct3ctf2/tinfx.tga       
        blendFunc add
		tcGen environment
        rgbGen identity
	}  
}

//LIGHT TUBES (SHADER BY PHANTAZM11)

textures/ct_ct3ctf2/blue_tube
{
	qer_editorimage textures/ct_ct3ctf2/blue_tube.tga
	q3map_globaltexture
        surfaceparm nomarks
	q3map_surfacelight 400
    cull disable
	{
        	map textures/ct_ct3ctf2/blue_tube.tga
    }
}

textures/ct_ct3ctf2/red_tube
{
	qer_editorimage textures/ct_ct3ctf2/red_tube.tga
	q3map_globaltexture
        surfaceparm nomarks
	q3map_surfacelight 400
    cull disable
	{
        	map textures/ct_ct3ctf2/red_tube.tga
    }
}

//PIPELIQUID

textures/ct_ct3ctf2/blue_pipe_liquid
{
		qer_editorimage textures/ct_ct3ctf2/water_1.tga
		q3map_globaltexture
		surfaceparm nomarks
		cull disable
		q3map_surfacelight 300
		q3map_lightsubdivide 32
		q3map_lightimage textures/ct_ct3ctf2/blue_tube.tga
		{
			map textures/ct_ct3ctf2/blue_tube.tga
			blendFunc blend
		}
		{ 
			map textures/ct_ct3ctf2/water_1.tga
			blendFunc GL_dst_color GL_one
			rgbgen identity
			tcmod scale .5 .5
			tcmod scroll -.05 .001
		}
	
		{ 
			map textures/ct_ct3ctf2/water_2.tga
			blendFunc GL_dst_color GL_one
			rgbgen identity
			tcmod scale .5 .5
			tcmod scroll .025 -.001
		}

		{ 
			map textures/ct_ct3ctf2/water_3.tga
			blendFunc GL_dst_color GL_one
			rgbgen identity
			tcmod scale .25 .5
			tcmod scroll .001 .025
		}	
}

textures/ct_ct3ctf2/red_pipe_liquid
{
		qer_editorimage textures/ct_ct3ctf2/water_1.tga
		q3map_globaltexture
		surfaceparm nomarks
		cull disable
		q3map_surfacelight 300
		q3map_lightsubdivide 32
		q3map_lightimage textures/ct_ct3ctf2/red_tube.tga
		{
			map textures/ct_ct3ctf2/red_tube.tga
			blendFunc GL_ONE GL_ZERO
		}
		{ 
			map textures/ct_ct3ctf2/water_1.tga
			blendFunc GL_dst_color GL_one
			rgbgen identity
			tcmod scale .5 .5
			tcmod scroll -.05 .001
		}
	
		{ 
			map textures/ct_ct3ctf2/water_2.tga
			blendFunc GL_dst_color GL_one
			rgbgen identity
			tcmod scale .5 .5
			tcmod scroll .025 -.001
		}

		{ 
			map textures/ct_ct3ctf2/water_3.tga
			blendFunc GL_dst_color GL_one
			rgbgen identity
			tcmod scale .25 .5
			tcmod scroll .001 .025
		}	
}

//TRIMS

textures/ct_ct3ctf2/stair_trim_blue
{
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3ctf2/stair_trim_blue.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3ctf2/stair_trim_blue_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_ct3ctf2/stair_trim_red
{
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3ctf2/stair_trim_red.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3ctf2/stair_trim_red_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_ct3ctf2/light_trim_blue
{
	surfaceparm nomarks
	q3map_surfacelight 1000
	q3map_lightSubdivide 64
	q3map_backSplash 0.1 24
	q3map_lightimage textures/ct_ct3ctf2/blue_tube.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3ctf2/light_trim_blue.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3ctf2/light_trim_blue_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_ct3ctf2/light_trim_red
{
	surfaceparm nomarks
	q3map_surfacelight 1000
	q3map_lightSubdivide 64
	q3map_backSplash 0.1 24
	q3map_lightimage textures/ct_ct3ctf2/red_tube.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3ctf2/light_trim_red.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3ctf2/light_trim_red_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_ct3ctf2/large_trim_blue
{
	qer_editorimage textures/ct_ct3ctf2/large_trim_blue.tga
	//surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3ctf2/large_trim_blue.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3ctf2/large_trim_blue_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_ct3ctf2/large_trim_red
{
	qer_editorimage textures/ct_ct3ctf2/large_trim_red.tga
	//surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ct3ctf2/large_trim_red.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ct3ctf2/large_trim_red_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_ct3ctf2/metal_trim
{   
        qer_editorimage textures/ct_ct3ctf2/metal_trim.tga
	{
		map textures/ct_ct3ctf2/metal_trim.tga
		rgbGen identity
	}
	{
        map textures/ct_ct3ctf2/tinfx.tga       
        blendFunc add
		tcGen environment
        rgbGen identity
	}   
    {
		map $lightmap
        blendFunc GL_DST_COLOR GL_ONE_MINUS_DST_ALPHA
		rgbGen identity
	}
}

textures/ct_ct3ctf2/baremetal_01_shiny
{   
        qer_editorimage textures/ct_ct3ctf2/baremetal_01.tga
	{
		map textures/ct_ct3ctf2/baremetal_01.tga
		tcMod scale 2 2
		rgbGen identity
	}
	{
        map textures/ct_ct3ctf2/tinfx.tga       
        blendFunc add
		tcGen environment
        rgbGen identity
	}   
    {
		map $lightmap
        blendFunc GL_DST_COLOR GL_ONE_MINUS_DST_ALPHA
		rgbGen identity
	}
}

textures/ct_ct3ctf2/trim_02_shiny
{   
        qer_editorimage textures/ct_ct3ctf2/trim_02.tga
	{
		map textures/ct_ct3ctf2/trim_02.tga
		rgbGen identity
	}
	{
        map textures/ct_ct3ctf2/tinfx.tga       
        blendFunc add
		tcGen environment
        rgbGen identity
	}   
    {
		map $lightmap
        blendFunc GL_DST_COLOR GL_ONE_MINUS_DST_ALPHA
		rgbGen identity
	}
}

//DECALS

//BLUE

textures/ct_ct3ctf2/blue_base
{
	qer_editorimage textures/ct_ct3ctf2/blue_base.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/blue_base.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/blue_perimeter
{
	qer_editorimage textures/ct_ct3ctf2/blue_perimeter.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/blue_perimeter.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/blue_center
{
	qer_editorimage textures/ct_ct3ctf2/blue_center.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/blue_center.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/blue_fd
{
	qer_editorimage textures/ct_ct3ctf2/blue_fd.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/blue_fd.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/blue_stripes
{
	qer_editorimage textures/ct_ct3ctf2/blue_stripes.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/blue_stripes.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/blue_YA
{
	qer_editorimage textures/ct_ct3ctf2/blue_YA.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/blue_YA.tga
		rgbGen identity
		blendFunc add
	}
}


textures/ct_ct3ctf2/blue_base_2
{
	qer_editorimage textures/ct_ct3ctf2/blue_base_2.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/blue_base_2.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/blue_arrow
{
	qer_editorimage textures/ct_ct3ctf2/blue_arrow.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/blue_arrow.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/blue_arrows
{
	qer_editorimage textures/ct_ct3ctf2/blue_arrows.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/blue_arrows.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/blue_arrows_2
{
	qer_editorimage textures/ct_ct3ctf2/blue_arrows_2.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/blue_arrows_2.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/blue_exit
{
	qer_editorimage textures/ct_ct3ctf2/blue_exit.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/blue_exit.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/MH_blue
{
	qer_editorimage textures/ct_ct3ctf2/MH_blue.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/MH_blue.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/RA_blue
{
	qer_editorimage textures/ct_ct3ctf2/RA_blue.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/RA_blue.tga
		rgbGen identity
		blendFunc add
	}
}

//RED--------------------------------------------------------------------------------------------------------------------------

textures/ct_ct3ctf2/red_base
{
	qer_editorimage textures/ct_ct3ctf2/red_base.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/red_base.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/red_perimeter
{
	qer_editorimage textures/ct_ct3ctf2/red_perimeter.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/red_perimeter.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/red_center
{
	qer_editorimage textures/ct_ct3ctf2/red_center.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/red_center.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/red_fd
{
	qer_editorimage textures/ct_ct3ctf2/red_fd.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/red_fd.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/red_stripes
{
	qer_editorimage textures/ct_ct3ctf2/red_stripes.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/red_stripes.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/red_YA
{
	qer_editorimage textures/ct_ct3ctf2/red_YA.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/red_YA.tga
		rgbGen identity
		blendFunc add
	}
}


textures/ct_ct3ctf2/red_base_2
{
	qer_editorimage textures/ct_ct3ctf2/red_base_2.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/red_base_2.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/red_arrow
{
	qer_editorimage textures/ct_ct3ctf2/red_arrow.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/red_arrow.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/red_arrows
{
	qer_editorimage textures/ct_ct3ctf2/red_arrows.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/red_arrows.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/red_arrows_2
{
	qer_editorimage textures/ct_ct3ctf2/red_arrows_2.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/red_arrows_2.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/red_exit
{
	qer_editorimage textures/ct_ct3ctf2/red_exit.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/red_exit.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/MH_red
{
	qer_editorimage textures/ct_ct3ctf2/MH_red.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/MH_red.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/RA_red
{
	qer_editorimage textures/ct_ct3ctf2/RA_red.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/RA_red.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/blue_fluorescent
{
	qer_editorimage textures/ct_ct3ctf2/blue_fluorescent.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/blue_fluorescent.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/blue_fluorescent_scroll
{
	qer_editorimage textures/ct_ct3ctf2/blue_fluorescent.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/blue_fluorescent.tga
		rgbGen identity
		blendFunc add
		tcmod scroll 0.05 0
	}
}

textures/ct_ct3ctf2/red_fluorescent
{
	qer_editorimage textures/ct_ct3ctf2/red_fluorescent.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/red_fluorescent.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/red_fluorescent_scroll
{
	qer_editorimage textures/ct_ct3ctf2/red_fluorescent.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/red_fluorescent.tga
		rgbGen identity
		blendFunc add
		tcmod scroll 0.05 0
	}
}

textures/ct_ct3ctf2/red_center_2
{
	qer_editorimage textures/ct_ct3ctf2/red_center_2.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/red_center_2.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/blue_center_2
{
	qer_editorimage textures/ct_ct3ctf2/blue_center_2.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/blue_center_2.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/red_fluorescent_2
{
	qer_editorimage textures/ct_ct3ctf2/fluorescent_2_red.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/fluorescent_2_red.tga
		rgbGen identity
		blendFunc add
	}
}

textures/ct_ct3ctf2/blue_fluorescent_2
{
	qer_editorimage textures/ct_ct3ctf2/fluorescent_2_blue.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/fluorescent_2_blue.tga
		rgbGen identity
		blendFunc add
	}
}

//JUMPPAD WALL

textures/ct_ct3ctf2/blue_jumppad_wall
{
	qer_editorimage textures/ct_ct3ctf2/jumppad_wall.tga
	q3map_surfacelight 60
	q3map_lightimage textures/ct_ct3ctf2/blue_tube.tga
	{
	map textures/ct_ct3ctf2/black.tga
	rgbGen identity
	}
	{
		map textures/ct_ct3ctf2/blue_jumppad_wall_arrows.tga
		blendfunc GL_ONE GL_ONE
		rgbGen identity
		//tcMod stretch sin 1 .01 0 1
		tcmod scroll 0 .25
	}

	{
		map textures/ct_ct3ctf2/jumppad_wall.tga
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

textures/ct_ct3ctf2/red_jumppad_wall
{
	qer_editorimage textures/ct_ct3ctf2/jumppad_wall.tga
	q3map_surfacelight 60
	q3map_lightimage textures/ct_ct3ctf2/red_tube.tga
	{
	map textures/ct_ct3ctf2/black.tga
	rgbGen identity
	}
	{
		map textures/ct_ct3ctf2/red_jumppad_wall_arrows.tga
		blendfunc GL_ONE GL_ONE
		rgbGen identity
		//tcMod stretch sin 1 .01 0 1
		tcmod scroll 0 .25
	}

	{
		map textures/ct_ct3ctf2/jumppad_wall.tga
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

//GRATE

textures/ct_ct3ctf2/grate_01
{
	surfaceparm	metalsteps	
    surfaceparm trans		
	surfaceparm nonsolid
	cull none
    nopicmip
	surfaceparm alphashadow
	{
		map textures/ct_ct3ctf2/grate_01.tga
		tcMod scale 2 2
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

textures/ct_ct3ctf2/msg
{
      surfaceparm nomarks 
      qer_editorimage textures/ct_ct3ctf2/ads/MaverickServers_1024x512.tga 
      nopicmip 
   {
      map textures/ct_ct3ctf2/ads/MaverickServers_1024x512.tga 
   }
}

textures/ct_ct3ctf2/kot_in_action
{
      surfaceparm nomarks 
      qer_editorimage textures/ct_ct3ctf2/ads/Kot-in-Action_logo_1024x512.tga 
      nopicmip 
   {
      map textures/ct_ct3ctf2/ads/Kot-in-Action_logo_1024x512.tga 
   }
}

textures/ct_ct3ctf2/lunar_module
{
      surfaceparm nomarks 
      qer_editorimage textures/ct_ct3ctf2/ads/LunarModule_logo4_512x128.tga 
      nopicmip 
   {
      map textures/ct_ct3ctf2/ads/LunarModule_logo4_512x128.tga 
   }
}

textures/ct_ct3ctf2/luxology
{
      surfaceparm nomarks 
      qer_editorimage textures/ct_ct3ctf2/ads/Luxology_white_1024x512.tga 
      nopicmip 
   {
      map textures/ct_ct3ctf2/ads/Luxology_white_1024x512.tga 
   }
}

textures/ct_ct3ctf2/massacreservers
{
      surfaceparm nomarks 
      qer_editorimage textures/ct_ct3ctf2/ads/MassacreServers_768x1024.tga 
      nopicmip 
   {
      map textures/ct_ct3ctf2/ads/MassacreServers_768x1024.tga 
   }
}

textures/ct_ct3ctf2/readyupradio
{
      surfaceparm nomarks 
      qer_editorimage textures/ct_ct3ctf2/ads/ReadyUpRadio_1024x512.tga 
      nopicmip 
   {
      map textures/ct_ct3ctf2/ads/ReadyUpRadio_1024x512.tga 
   }
}

textures/ct_ct3ctf2/sapphire
{
      surfaceparm nomarks 
      qer_editorimage textures/ct_ct3ctf2/ads/Sapphire_1024x1024.tga 
      nopicmip 
   {
      map textures/ct_ct3ctf2/ads/Sapphire_1024x1024.tga 
   }
}

textures/ct_ct3ctf2/steelstorm
{
      surfaceparm nomarks 
      qer_editorimage textures/ct_ct3ctf2/ads/Steel_Storm_1024x512.tga 
      nopicmip 
   {
      map textures/ct_ct3ctf2/ads/Steel_Storm_1024x512.tga 
   }
}

textures/ct_ct3ctf2/wacom_alpha
{
      surfaceparm nomarks 
      qer_editorimage textures/ct_ct3ctf2/ads/Wacom_512x512.tga 
      nopicmip 
   {
      map textures/ct_ct3ctf2/ads/Wacom_512x512_alpha.tga 
	  blendFunc GL_ONE GL_ZERO
	  alphaFunc GE128
   }
}

textures/ct_ct3ctf2/wacom
{
      surfaceparm nomarks 
      qer_editorimage textures/ct_ct3ctf2/ads/Wacom_512x512.tga 
      nopicmip 
   {
      map textures/ct_ct3ctf2/ads/Wacom_512x512.tga 
   }
}

textures/ct_ct3ctf2/black
{
      surfaceparm nomarks 
      qer_editorimage textures/ct_ct3ctf2/black.tga 
      nopicmip 
   {
      map textures/ct_ct3ctf2/black.tga 
   }
}

textures/ct_ct3ctf2/white
{
      surfaceparm nomarks 
      qer_editorimage textures/ct_ct3ctf2/white.tga 
      nopicmip 
   {
      map textures/ct_ct3ctf2/white.tga 
   }
}

//PU SPAWN

textures/ct_ct3ctf2/PU_spawn
{
	qer_editorimage textures/ct_ct3ctf2/PU_spawn_1.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_ct3ctf2/PU_spawn_1.tga
		rgbGen identity
		blendFunc add
		tcmod rotate 10
	}
	{
		map textures/ct_ct3ctf2/PU_spawn_2.tga
		rgbGen identity
		blendFunc add
		tcmod rotate 60
	}
	{
		map textures/ct_ct3ctf2/PU_spawn_3.tga
		rgbGen identity
		blendFunc add
		tcmod rotate 45
	}
}

//WATER

textures/ct_ct3ctf2/water_reflection
	{
		qer_editorimage textures/liquids/pool3d_3e.tga
		qer_trans .5
		surfaceparm trans
		surfaceparm nonsolid
		cull disable
		{ 
			map textures/liquids/pool3d_5e.tga
			blendFunc GL_dst_color GL_zero
			rgbgen identity
			tcmod scale .5 .5
			tcmod scroll .025 .01
		}
		{ 
			map textures/liquids/pool3d_3e.tga
			blendFunc GL_dst_color GL_zero
			tcmod scale -.5 -.5
			tcmod scroll .025 .025
		}
		{
			map $lightmap
			blendFunc GL_dst_color GL_zero
			rgbgen identity		
		}
}

textures/ct_ct3ctf2/waterfog
{
	qer_editorimage textures/sfx/fog_grey.tga
	surfaceparm	trans
	surfaceparm	nonsolid
	surfaceparm	fog
	surfaceparm 	nolightmap
	q3map_globaltexture
	q3map_surfacelight 100
		fogparms ( .220 .210 .200 ) 1800
	{
		map textures/liquids/kc_fogcloud3.tga
		blendfunc gl_dst_color gl_zero
		tcmod scale -.05 -.05
		tcmod scroll .01 -.01
		rgbgen identity
	}
	{
		map textures/liquids/kc_fogcloud3.tga
		blendfunc gl_dst_color gl_zero
		tcmod scale .05 .05
		tcmod scroll .01 -.01
		rgbgen identity
	}
}

//RED TP

textures/ct_ct3ctf2/red_tp
{
	surfaceparm nolightmap
	surfaceparm nonsolid
	cull twosided
	{
		map textures/ct_ct3ctf2/red_tp.tga
		tcGen environment
                tcMod turb 0 0.25 0 0.5
                tcmod scroll 1 1
		blendfunc GL_ONE GL_ONE
	}
}