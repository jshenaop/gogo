$(function(){
    console.log('hola mundo2');
var formularioEnvio = {};

var MAP_WIDTH  = 420;
var MAP_HEIGHT = 590;

var mapContainer = document.getElementById("human_body");
var map = new Raphael(mapContainer, MAP_WIDTH, MAP_HEIGHT);

var animationSpeed = 4000;

var style = {
  fill: "#00a6b9",
  stroke: "#00a6b9",
  "stroke-width": 1,
  "stroke-linejoin": "round",
  cursor: "pointer"
};

var hoverStyle = {
	fill: "#FC6604",
	stroke: "#FC6604"
}

var regions = {};
regions["cabeza"] = map.path('M 228.7 45 L 227.9 32 L 217.7 21.7 L 208.4 20.5 L 199 21.7 L 188.8 32 L 188.1 45 L 183.9 47.4 L 188.1 58 L 190 58.7 L 190.1 71.1 L 193.5 77.7 L 199.5 67.2 L 196.9 58.3 L 202.7 60.8 L 208.4 59.4 L 214 60.8 L 219.8 58.3 L 217.2 67.2 L 223.2 77.7 L 226.6 71.1 L 226.8 58.7 L 228.7 58 L 232.8 47.4 L 228.7 45');
regions["trapecio-der"] = map.path('M 214 61.9 L 210.2 64.2 L 209.7 75.8 L 213.2 89.2 L 214.4 111 L 230.4 106.7 L 245.8 105.2 L 217 83.5 L 213.1 72.2 L 214 61.9');
regions["trapecio-izq"] = map.path('M 202.7 61.9 L 206.5 64.2 L 207.1 75.8 L 203.5 89.2 L 202.4 111 L 186.4 106.7 L 170.9 105.2 L 199.7 83.5 L 203.7 72.2 L 202.7 61.9');
regions["redondo-menor-der"] = map.path('M 263.5 111 L 244.5 117.4 L 233.9 145.2 L 213.8 164 L 215.3 132.8 L 215.1 118.7 L 244.3 108.2 L 263.5 111');
regions["redondo-menor-izq"] = map.path('M 153.3 111 L 172.3 117.4 L 182.8 145.2 L 202.9 164 L 201.4 132.8 L 201.6 118.7 L 172.5 108.2 L 153.3 111');
regions["redondo-mayor-der"] = map.path('M 254.8 125.9 L 248 125.9 L 238.3 151.6 L 265.7 147.9 L 265.2 137.7 L 254.8 125.9');
regions["redondo-mayor-izq"] = map.path('M 161.9 125.9 L 168.7 125.9 L 178.5 151.6 L 151 147.9 L 151.6 137.7 L 161.9 125.9');
regions["deltoides-der"] = map.path('M 270.6 115.1 L 253.3 118.5 L 281.1 150.5 L 283.8 135.4 L 270.6 115.1');
regions["deltoides-izq"] = map.path('M 146.1 115.1 L 163.4 118.5 L 135.6 150.5 L 133 135.4 L 146.1 115.1');
regions["triceps-der"] = map.path('M 265.9 184 L 269.8 145.6 L 290.8 167.1 L 289.3 199.8 L 277.9 205.2 L 265.9 184');
regions["triceps-izq"] = map.path('M 150.8 184 L 146.9 145.6 L 125.9 167.1 L 127.4 199.8 L 138.8 205.2 L 150.8 184');
regions["supinador-der"] = map.path('M 283.3 205 L 290.4 215.8 L 290.1 234.8 L 300.9 261.6 L 282.3 239.3 L 271.8 212.5 L 276.6 216 L 280.3 214.5 L 283.3 205');
regions["supinador-izq"] = map.path('M 133.4 205 L 126.4 215.8 L 126.6 234.8 L 115.8 261.6 L 134.4 239.3 L 144.9 212.5 L 140.2 216 L 136.4 214.5 L 133.4 205');
regions["palmar-der"] = map.path('M 295.4 209.2 L 293.4 217 L 296.2 243.1 L 315 280 L 321.7 269.7 L 314.2 257.4 L 302.9 214.8 L 295.4 209.2');
regions["palmar-izq"] = map.path('M 121.4 209.2 L 123.4 217 L 120.6 243.1 L 101.8 280 L 95 269.7 L 102.5 257.4 L 113.8 214.8 L 121.4 209.2');
regions["mano-der"] = map.path('M 324.5 277.2 L 321.2 285 L 311.7 286.5 L 311 300.5 L 316 320.6 L 319.2 320.3 L 316.1 307 L 319.5 306.9 L 324.8 321.1 L 328.8 320.6 L 323.8 306.2 L 327.3 305.6 L 334 320.8 L 339.1 320.3 L 332.2 304.4 L 334.5 303 L 343.1 316.6 L 347.3 316.1 L 334.5 291.7 L 335.8 289.7 L 347.8 294.8 L 348.6 292 L 338.8 283.2 L 324.5 277.2');
regions["mano-izq"] = map.path('M 92.3 277.2 L 95.5 285 L 105.1 286.5 L 105.8 300.5 L 100.8 320.6 L 97.5 320.3 L 100.7 307 L 97.3 306.9 L 92 321.1 L 88 320.6 L 93 306.2 L 89.5 305.6 L 82.7 320.8 L 77.7 320.3 L 84.6 304.4 L 82.2 303 L 73.7 316.6 L 69.4 316.1 L 82.2 291.7 L 81 289.7 L 68.9 294.8 L 68.2 292 L 78 283.2 L 92.3 277.2');
regions["dorsal-der"] = map.path('M 265.5 150.9 L 237.1 156.5 L 214.2 178.3 L 211.4 259.2 L 236.9 235.7 L 265.7 157.1 L 265.5 150.9');
regions["dorsal-izq"] = map.path('M 151.2 150.9 L 179.6 156.5 L 202.5 178.3 L 205.4 259.2 L 179.8 235.7 L 151 157.1 L 151.2 150.9');
regions["oblicuo-der"] = map.path('M 249.4 213.3 L 241.5 231.6 L 241.3 239.3 L 251.8 242.7 L 249.4 213.3');
regions["oblicuo-izq"] = map.path('M 167.4 213.3 L 175.3 231.6 L 175.5 239.3 L 164.9 242.7 L 167.4 213.3');
regions["gluteo-med-der"] = map.path('M 250.9 247.7 L 255.2 273.1 L 243.5 256.9 L 229.2 250 L 237.5 241.5 L 250.9 247.7');
regions["gluteo-med-izq"] = map.path('M 165.9 247.7 L 161.5 273.1 L 173.2 256.9 L 187.5 250 L 179.2 241.5 L 165.9 247.7');
regions["gluteo-der"] = map.path('M 226.4 255.4 L 223 263.9 L 212.1 270.9 L 211.2 294 L 238.3 306.8 L 249.9 319.2 L 256.1 302.7 L 255.2 280.8 L 244.8 263 L 226.4 255.4');
regions["gluteo-izq"] = map.path('M 190.3 255.4 L 193.7 263.9 L 204.6 270.9 L 205.6 294 L 178.5 306.8 L 166.8 319.2 L 160.6 302.7 L 161.5 280.8 L 171.9 263 L 190.3 255.4');
regions["bicep-fem-der"] = map.path('M 242 346.1 L 239 385 L 225.8 417.8 L 219.1 402 L 221.8 369.8 L 214.7 331.8 L 214.7 298.9 L 227 307.5 L 236.2 311.9 L 242 346.1');
regions["bicep-fem-izq"] = map.path('M 202 331.8 L 194.5 367.3 L 194.8 368.3 L 197.7 402 L 190.9 417.8 L 177.7 385 L 174.7 346.1 L 180.5 311.9 L 190.7 307 L 202 298.9 L 202 331.8');
regions["bicep-fem-alto-der"] = map.path('M 259.5 313.9 L 258.4 361 L 252.2 380.1 L 249.9 408.2 L 242.6 380.3 L 247.5 365.1 L 242.4 319.2 L 250.5 323.6 L 258 310 L 259.5 313.9');
regions["bicep-fem-alto-izq"] = map.path('M 169.3 365.1 L 174.1 380.3 L 166.8 408.2 L 164.6 380.1 L 158.9 362.6 L 158.8 358.9 L 157.2 313.9 L 158.7 310 L 165.7 323.9 L 174.3 319.2 L 169.3 365.1');
regions["peroneo-der"] = map.path('M 235.4 405.2 L 234.1 473.1 L 222.5 486.2 L 216.8 477.8 L 216.4 459.5 L 221.5 432.2 L 235.4 405.2');
regions["peroneo-izq"] = map.path('M 181.3 405.2 L 182.6 473.1 L 194.3 486.2 L 199.9 477.8 L 200.3 459.5 L 195.2 432.2 L 181.3 405.2');
regions["gastrocnemio-der"] = map.path('M 239 401.2 L 239.8 456.7 L 236.6 477.8 L 242 482.3 L 251.6 462.7 L 249.2 424.9 L 244.5 409.5 L 244.1 398.4 L 239 401.2');
regions["gastrocnemio-izq"] = map.path('M 177.7 401.2 L 177 456.7 L 180.2 477.8 L 174.7 482.3 L 165.1 462.7 L 167.6 424.9 L 172.3 409.5 L 172.6 398.4 L 177.7 401.2');
regions["tendon-aquiles-der"] = map.path('M 237.3 554.7 L 238.4 559.4 L 235.4 561.6 L 230.2 560.1 L 227.3 561.6 L 225.7 524.8 L 221.7 496.9 L 222.8 490.5 L 235.1 480.2 L 240.5 485.1 L 241.8 528.2 L 237.3 554.7');
regions["tendon-aquiles-izq"] = map.path('M 195 496.9 L 191.1 524.8 L 189.4 561.6 L 186.6 560.1 L 181.3 561.6 L 178.3 559.4 L 179.4 554.7 L 174.9 528.2 L 176.2 485.1 L 181.7 480.2 L 193.9 490.5 L 195 496.9');
regions["talon-der"] = map.path('M 240.5 559.6 L 235.5 563.8 L 227.2 563.1 L 223.4 558.8 L 219.2 564.8 L 224.2 568.1 L 236.2 570.6 L 245.8 560.6 L 244.3 556.6 L 240.5 559.6');
regions["talon-izq"] = map.path('M 176.3 559.6 L 181.3 563.8 L 189.6 563.1 L 193.3 558.8 L 197.6 564.8 L 192.6 568.1 L 180.5 570.6 L 171 560.6 L 172.5 556.6 L 176.3 559.6');

var chusque = 0 ;
for(var regionName in regions) {
	chusque += 1 ;
	chusque.toString();
    estilo(regionName,regions[regionName],chusque);
}

function estilo(regionName,region,chusque){
	  region.attr(style);
	  var toque = false ;
	  	region[0].addEventListener("click", function() {
	  		toque = !toque;
            var select = $('select[name = '+chusque+']');
	  		if(toque){
                console.log('soy un toque');
                console.log(toque);
                console.log(region[0]);
	  			region.animate(hoverStyle);
                region.active = true;
                ///PARA LLENAR EL FORMULARIO
                //  $('#'+chusque).modal();
                //  select.change(function(){
                //       formularioEnvio[String(regionName)]= $(this).val();
                //       var stringFormularioEnvio = JSON.stringify(formularioEnvio);
                //       $('#formularioEnvio').val(stringFormularioEnvio);
                //  })
	  		}else{
	  			region.animate(style);
                select.val('');
                // delete formularioEnvio[String(regionName)];
                // var stringFormularioEnvio = JSON.stringify(formularioEnvio);
                // $('#formularioEnvio').val(stringFormularioEnvio);
	  		}
        }, true);
    //    fin funcion estilo
      	}

// $(window).on('click',function(){
    // var chusque2 = 0;
    // for(var regionName in regions){
    //     chusque2 += 1;
    //     var select = $('select[name = '+chusque2+']');
    //     var valorSelect = select.val();
    //     if(valorSelect == ''){
    //         var region = regions[regionName];
    //         region.attr(style);
    //
    //     }
    // }
// })

});
