textures/jk_tourney1/runway_dblue
{
	q3map_lightimage textures/jk_tourney1/runway_glow_dblue.tga
	surfaceparm nomarks
	q3map_surfacelight 400
	{
		map textures/jk_tourney1/runway_glow_dblue.tga
		tcmod scale 1 .25
		rgbgen wave square -1 2 .5 8
		tcmod scroll 0 .5
	}	

	{
		map textures/jk_tourney1/runway_dblue.tga
		blendfunc blend
		rgbGen identity
	}
        
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
	}

	{
		map textures/jk_tourney1/runwayb_dblue.tga
		blendfunc add
		rgbGen identity
	}

	
}


textures/jk_tourney1/jk_toxicsky_dm1
{
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm sky
        
        q3map_lightsubdivide 512
	q3map_surfacelight 280
	q3map_sun  1 1 0.5 110 90 70
        
	qer_editorimage textures/jk_tourney1/jk_toxicsky_dm1.tga
	skyparms - 256 -
	{
		map textures/jk_tourney1/jk_inteldimclouds.tga
		tcMod scroll 0.03 0.03
		tcMod scale 3 2
		depthWrite
	}
	{
		map textures/jk_tourney1/jk_intelredclouds.tga
		blendfunc add
		tcMod scroll 0.01 0.01
		tcMod scale 3 3
	}
}


textures/jk_tourney1/jk_q3redflag
{
     cull disable
     surfaceparm alphashadow
     surfaceparm trans	
     surfaceparm nomarks
     tessSize 64
     deformVertexes wave 30 sin 0 3 0 .2
     deformVertexes wave 100 sin 0 3 0 .7
     
        {
                map textures/jk_tourney1/jk_q3redflag.tga
                alphaFunc GE128
		depthWrite
		rgbGen vertex
        }
        {
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}


}

textures/jk_tourney1/jk_bouncepad_floor1
{

	//q3map_surfacelight 2000
	surfaceparm nodamage
	q3map_lightimage textures/jk_tourney1/jk_jumppadsmall.tga	
	q3map_surfacelight 400

	
	{
		map textures/jk_tourney1/jk_bouncepad_floor1.tga
		rgbGen identity
	}
	
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
	}
	
	{
		map textures/jk_tourney1/jk_bouncepad_layer1.tga
		blendfunc add
		rgbGen wave sin .5 .5 0 1.5	
	}

	{
		clampmap textures/jk_tourney1/jk_jumppadsmall.tga
		blendfunc add
		tcMod stretch sin 1.2 .8 0 1.5
		rgbGen wave square .5 .5 .25 1.5
	}

	//	END
}


textures/jk_tourney1/jkt1_q3abanner
{
	qer_editorimage textures/jk_tourney1/jkt1_q3abanner.tga
        q3map_lightimage textures/jk_tourney1/ss_jkt1_golgothabanner.tga
        q3map_surfacelight 100


        {
		animMap 0.40 textures/jk_tourney1/jkt1_q3abanner.tga textures/jk_tourney1/ss_jkt1_golgothabanner.tga textures/jk_tourney1/jkt1_powzerbanner.tga
		//blendfunc add
		rgbGen wave square 0 3 0 .40
	}

	{
		map textures/base_wall/comp3text.tga
		blendfunc add
	        rgbGen identity
		tcmod scroll 3 3
	}

	{
		map textures/base_wall/comp3textb.tga
		blendfunc add
	        rgbGen identity
		tcmod scroll 3 3
	}


	{
		map $lightmap
	        rgbGen identity
		blendfunc filter
	}

	{
		map $lightmap
		tcgen environment
		tcmod scale .5 .5
	        rgbGen wave sin .25 0 0 0
		blendfunc add
	}	          		
}  


   
textures/jk_tourney1/jk_t1fog_test
{
  
     qer_editorimage textures/jk_tourney1/jk_t1fog_test.tga
     surfaceparm     trans
     surfaceparm     nonsolid
     surfaceparm     fog
     surfaceparm     nodrop
     surfaceparm     nolightmap

     fogparms ( .85 .10 .01 ) 980 

        {
		map textures/jk_tourney1/jkt1_fogcloud3_test.tga
		blendfunc filter
		tcmod scale -.05 -.05
		tcmod scroll .01 -.01
		rgbgen identity
	}

	{
		map textures/jk_tourney1/jkt1_fogcloud3_test.tga
		blendfunc filter
		tcmod scale .05 .05
		tcmod scroll .01 -.01
		rgbgen identity
	}

}


textures/jk_tourney1/jk_bluemetal3b_trans
{
	qer_editorimage textures/jk_tourney1/jk_bluemetal3b_trans.tga
	surfaceparm nonsolid
        
        {
               map $lightmap
               rgbGen identity
        } 


        {     
               map textures/jk_tourney1/jk_bluemetal3b_trans.tga
               rgbGen identity
               blendfunc filter
        }	

}