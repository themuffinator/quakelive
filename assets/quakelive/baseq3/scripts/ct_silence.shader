//JUMPPAD WALL

textures/ct_silence/wall_jump
{
	qer_editorimage textures/ct_silence/wall_jump.tga

	{
		map textures/ct_silence/rlaunch3_green.tga
		rgbGen identity
		tcmod scale 1 .5
		tcmod scroll 0 1.42
	}

	{
		map textures/ct_silence/wall_jump.tga
		blendFunc blend
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc GL_DST_COLOR GL_ZERO
	}	
}

//********************************************************************************************************************************************

//LIGHTS

textures/ct_silence/ceil1_38_5k
{
	qer_editorimage textures/base_light/ceil1_38.tga
	surfaceparm nomarks
	q3map_surfacelight 5000
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/base_light/ceil1_38.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/base_light/ceil1_38.blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_silence/ceil_cyan
{
	qer_editorimage textures/base_light/ceil1_34.tga
	surfaceparm nomarks
	q3map_surfacelight 10
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/base_light/ceil1_34.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/base_light/ceil1_34.blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_silence/ceil_yellow
{
	qer_editorimage textures/ct_silence/ceil1_yellow.tga
	surfaceparm nomarks
	q3map_surfacelight 10
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_silence/ceil1_yellow.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_silence/ceil1_yellow.blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_silence/ceil_yellow_2k
{
	qer_editorimage textures/ct_silence/ceil1_yellow.tga
	q3map_surfacelight 2000
	q3map_lightimage textures/ct_silence/yellow.tga
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_silence/ceil1_yellow.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_silence/ceil1_yellow.blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_silence/ceil_green_5k
{
	qer_editorimage textures/ct_silence/ceil1_green.tga
	q3map_surfacelight 1000
	q3map_lightimage textures/ct_silence/green.tga
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_silence/ceil1_green.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_silence/ceil1_green.blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_silence/ceil_yellow_7k
{
	qer_editorimage textures/ct_silence/ceil1_yellow.tga
	q3map_surfacelight 7000
	q3map_lightimage textures/ct_silence/yellow.tga
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_silence/ceil1_yellow.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_silence/ceil1_yellow.blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_silence/ceil_white
{
	qer_editorimage textures/base_light/ceil1_38.tga
	surfaceparm nomarks
	q3map_surfacelight 10
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/base_light/ceil1_38.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/base_light/ceil1_38.blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_silence/circle_lamp_5k
{
	surfaceparm nomarks
	q3map_surfacelight 5000
	q3map_lightimage textures/ct_silence/lamp_01_blend.tga
	qer_editorimage textures/ct_silence/lamp_01.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_silence/lamp_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_silence/lamp_01_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

//********************************************************************************************************************************************

//LIQUIDS

textures/ct_silence/pipe_liquid
{
		qer_editorimage textures/liquids/pool3d_3.tga
		q3map_globaltexture
		surfaceparm nomarks
		cull disable
		q3map_surfacelight 100
		q3map_lightsubdivide 32
		q3map_lightimage textures/ct_silence/green.tga
	
		{
			map textures/ct_silence/green.tga
		}
		{ 
			map textures/liquids/pool3d_5.tga
			blendFunc GL_dst_color GL_one
			rgbgen identity
			tcmod scale .5 .5
			tcmod scroll -.05 .001
		}
	
		{ 
			map textures/liquids/pool3d_6.tga
			blendFunc GL_dst_color GL_one
			rgbgen identity
			tcmod scale .5 .5
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
			map textures/effects/tinfx.tga
            tcgen environment
			blendFunc GL_ONE GL_ONE
			rgbGen identity
		}
		{
			map $lightmap
			blendFunc filter
			//blendFunc GL_dst_color GL_zero
			rgbgen identity		
	}   
}
	
//GREEN FLAG

textures/ct_silence/greenflag
{
        tessSize 64
        deformVertexes wave 194 sin 0 3 0 .4
        deformVertexes normal .5 .1
        surfaceparm nomarks
        cull none
    
	{
		map textures/ct_silence/greenflag.tga
		rgbGen identity
	}
    
	{
		map textures/effects/spawnarmormap2.tga
                tcGen environment
                tcmod scale 9 3
                tcmod scroll .1 .7
                
                blendFunc GL_ONE GL_ONE
                rgbGen identity
	}
    
	{
		map textures/ct_silence/greenflag.tga
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

//JUMPPAD

textures/ct_silence/jumppad_green
{
	q3map_lightimage textures/ct_silence/green.tga
	qer_editorimage textures/ct_silence/jumppadsmall_green.tga
	surfaceparm nomarks
	q3map_surfacelight 1000
	light 1
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_silence/jumppad_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		clampmap textures/ct_silence/jumppadsmall_green.tga
		blendfunc add
		tcMod stretch sin 1.2 1.75 0 1.2
		//rgbGen wave square .5 .5 .25 1.2
	}
}

//QUAD SPAWN

textures/ct_silence/quad_spawn
{
	qer_editorimage textures/ct_silence/quad_spawn.tga
	{
		map textures/ct_silence/quad_spawn.tga
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc GL_DST_COLOR GL_ZERO
	}
	{
		map textures/ct_silence/quad_spawn_glow.tga
		blendFunc GL_ONE GL_ONE
		rgbGen wave sin .5 .5 0 .5	
		depthfunc equal
	}
}