//-----------------------------------------------------------------
//-----Tom 'Phantazm11' Perryman
//-----www.phantazm11.com
//-----phantazm11(at)gmail[dot]com
//-----08.10.2012
//-----------------------------------------------------------------

textures/phantq3dm5/solarium_sky

{
	q3map_lightImage env/phantq3dm5/solarium_ft.tga

	q3map_sunExt 1 1 1 200 90 70 3 32//red green blue intensity degrees elevation
	//q3map_sunExt 1 1 1 150 -35 33 3 32	
	q3map_lightmapFilterRadius 0 8
	q3map_skyLight 100 6

	surfaceparm sky
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm nodlight

	nopicmip
	nomipmaps

	qer_editorimage env/phantq3dm5/solarium_ft.tga

	skyparms env/phantq3dm5/solarium - -

}

textures/phantq3dm5/phant_solarium_window_01
{
	qer_editorimage textures/phantq3dm5/phant_solarium_window_01.tga
	qer_trans 25	
	surfaceparm alphashadow		
	//surfaceparm nonsolid
	surfaceparm trans
	surfaceparm nomarks	
	{
		map textures/phantq3dm5/phant_solarium_window_01.tga
		blendFunc filter
		rgbGen identity
	}		
	{
		map textures/phantq3dm5/phant_solarium_window_01.tga
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

textures/phantq3dm5/phant_solarium_window_02
{
	qer_editorimage textures/phantq3dm5/phant_solarium_window_02.tga
	q3map_surfacelight 215
	nopicmip
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantq3dm5/phant_solarium_window_02.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/phantq3dm5/phant_solarium_window_02_add.tga
		blendFunc GL_ONE GL_ONE
	}
}

textures/phantq3dm5/phant_solarium_water
{
              
	qer_editorimage textures/phantq3dm5/phant_solarium_water.tga
	q3map_globaltexture
	qer_trans .80
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm water
	cull disable
	nopicmip
	{
		map textures/phantq3dm5/phant_solarium_water.tga
		blendfunc GL_ONE GL_ONE //SRC_COLOR
		tcMod scroll .01 .01
                       
	}
	//{
	//	map textures/liquids/proto_poolpass.tga
	//	blendfunc GL_ONE GL_ONE
	//	tcMod scale .5 .6
	//	tcMod scroll .02 .03
	//}
	{
		map textures/phantq3dm5/phant_solarium_water.tga
		blendfunc GL_ONE GL_ONE
		tcMod scale .5 .6
		tcMod scroll .01 .02
	}
	{
		map $lightmap
		rgbgen identity
		blendfunc GL_DST_COLOR GL_ZERO
        }
               
		

}

textures/phantq3dm5/phant_solarium_fog
{
	qer_editorimage textures/phantq3dm5/phant_solarium_fog.tga
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nolightmap
	surfaceparm fog
	fogparms ( 0.5647058 0.5294117 0.3333333 ) 5000
	//fogparms ( 1.000000 0.905747 0.665528 ) 11000
	//fogparms ( .270 .258 .215 ) 1000
}

textures/phantq3dm5/solarium_sail
{
	cull disable
	surfaceparm alphashadow
	surfaceparm trans
	surfaceparm nomarks
	nopicmip
        {
                map textures/phantq3dm5/solarium_sail.tga
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

textures/phantq3dm5/phant_solarium_girder_01
{
	cull disable
	surfaceparm alphashadow
	surfaceparm trans
	surfaceparm nomarks
	nopicmip
        {
                map textures/phantq3dm5/phant_solarium_girder_01.tga
                alphaFunc GE128
		depthWrite
		//rgbGen vertex
        }
        {
		map $lightmap
		rgbGen identity
		blendFunc filter
		depthFunc equal
	}


}

textures/phantq3dm5/phant_solarium_ivy_1024
{
	surfaceparm nonsolid	
	surfaceparm alphashadow
	q3map_shadeangle 45
	cull none
	nopicmip
	deformVertexes wave 25 sin 3 2 0 0.1 
    	
	{
		map textures/phantq3dm5/phant_solarium_ivy_1024.tga
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identityLighting
	}

	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}

}

textures/phantq3dm5/phant_solarium_ivy_512
{
	surfaceparm nonsolid	
	surfaceparm alphashadow
	q3map_shadeangle 45
	cull none
	nopicmip
	deformVertexes wave 5 sin 2 .9 0 0.1 
    	
	{
		map textures/phantq3dm5/phant_solarium_ivy_512.tga
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identityLighting
	}

	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}

}


textures/phantq3dm5/phant_solarium_moss_1024
{
	surfaceparm nonsolid	
	surfaceparm alphashadow
	q3map_shadeangle 45
	cull none
	nopicmip
	   	
	{
		map textures/phantq3dm5/phant_solarium_moss_1024.tga
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identityLighting
	}

	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}

}

textures/phantq3dm5/phant_solarium_neon
{

	qer_editorimage textures/phantq3dm5/phant_solarium_neon.jpg
	surfaceparm nomarks
	q3map_surfacelight 500
        cull disable
	{
        	map textures/phantq3dm5/phant_solarium_neon.jpg
        }
 
}

textures/phantq3dm5/phant_solarium_neon_100
{

	qer_editorimage textures/phantq3dm5/phant_solarium_neon.jpg
	surfaceparm nomarks
	q3map_surfacelight 225
        cull disable
	{
        	map textures/phantq3dm5/phant_solarium_neon.jpg
        }
 
}

textures/phantq3dm5/tp_machine_light
{
	qer_editorimage textures/phantq3dm5/tp_machine_light.tga
        surfaceparm trans	
        surfaceparm nomarks
	q3map_surfacelight 150
	cull none
        nopicmip
	polygonoffset
	{
		map textures/phantq3dm5/tp_machine_light.tga
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{	map textures/phantq3dm5/tp_machine_light_add.tga
		blendFunc add
	}
}

textures/phantq3dm5/phant_solarium_flower_01
{
	surfaceparm nonsolid	
   	surfaceparm alphashadow
	q3map_shadeangle 45
   	cull none
	nopicmip
    	
	{
		map textures/phantq3dm5/phant_solarium_flower_01.tga
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identityLighting
	}

	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}

}

textures/phantq3dm5/phant_solarium_flower_02
{
	surfaceparm nonsolid	
	surfaceparm alphashadow
	q3map_shadeangle 45
	cull none
	nopicmip
    	
	{
		map textures/phantq3dm5/phant_solarium_flower_02.tga
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identityLighting
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}

}

textures/phantq3dm5/phant_solarium_leaves_512
{
	surfaceparm nonsolid	
	surfaceparm alphashadow
	q3map_shadeangle 45
	cull none
	nopicmip
    	
	{
		map textures/phantq3dm5/phant_solarium_leaves_512.tga
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identityLighting
	}

	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}

}

textures/phantq3dm5/phant_solarium_leaf_01
{
	surfaceparm nonsolid	
	surfaceparm alphashadow
	q3map_shadeangle 45
	cull none
	nopicmip
    	
	{
		map textures/phantq3dm5/phant_solarium_leaf_01.tga
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identityLighting
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}

}

textures/phantq3dm5/phant_solarium_leaf_02
{
	surfaceparm nonsolid	
	surfaceparm alphashadow
	q3map_shadeangle 45
	cull none
	nopicmip
    	
	{
		map textures/phantq3dm5/phant_solarium_leaf_02.tga
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identityLighting
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}

}

textures/phantq3dm5/phant_solarium_glass
{
   	qer_editorimage textures/phantq3dm5/phant_solarium_glass.tga
	surfaceparm nolightmap
	surfaceparm alphashadow
	cull disable
	nopicmip

   {
      map textures/effects/envmap2.tga
      tcGen environment
      tcmod scale 4 4
      rgbGen identity
      blendFunc GL_DST_COLOR GL_ONE
   }

   {
      map textures/phantq3dm5/phant_solarium_glass.tga
      blendFunc blend
      rgbGen identity
   }
}

textures/phantq3dm5/tp_wires_001
{
	cull disable
	surfaceparm alphashadow
	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nonsolid
	nopicmip
     	{
		map textures/phantq3dm5/tp_wires_001.tga
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identityLighting
	}

	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}

}

textures/phantq3dm5/solarium_weapon_marker_out
{
	qer_editorimage textures/phantq3dm5/solarium_weapon_marker_out.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	cull none
	nopicmip
	polygonOffset 	
	sort 6
	{
		clampmap textures/phantq3dm5/solarium_weapon_marker_out.tga
		blendfunc add
		tcmod rotate -25
	}
	{
		clampmap textures/phantq3dm5/solarium_weapon_marker_in.tga
		blendfunc add
		tcmod rotate 25
	}
}

textures/phantq3dm5/phant_solarium_teleporter
{
	qer_editorimage textures/phantq3dm5/phant_solarium_teleporter.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	q3map_surfacelight 215
	cull none
	nopicmip
	polygonOffset 	
	sort 6
	{
		map textures/phantq3dm5/phant_solarium_teleporter.tga
		blendfunc blend
	}
	{
		map textures/phantq3dm5/phant_solarium_teleporter_add.tga
		blendfunc add
	}
}

textures/phantq3dm5/tp_rustedvent_001
{	
     	surfaceparm trans	
   	surfaceparm nonsolid
        surfaceparm nomarks
	polygonoffset
	sort 6
	nopicmip
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantq3dm5/tp_rustedvent_001.tga
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

textures/phantq3dm5/tp_pipecap
{	
     	surfaceparm trans	
   	surfaceparm nonsolid
	surfaceparm nomarks
	polygonoffset
	sort 6
	nopicmip
	{
		map textures/phantq3dm5/tp_pipecap.tga
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

textures/phantq3dm5/tp_fan_rusted
{
	qer_editorimage textures/phantq3dm5/tp_fan_rusted.tga
        surfaceparm trans	
        surfaceparm nomarks	
	cull none
        nopicmip
	{
		clampmap textures/phantq3dm5/tp_fan_rusted.tga
		tcMod rotate 450
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