var slider = document.getElementById('slider');
var sliderMin = document.getElementById('slider-min');
var sliderMax = document.getElementById('slider-max');

var slider2 = document.getElementById('slider2');
var slider2Min = document.getElementById('slider2-min');
var slider2Max = document.getElementById('slider2-max');


noUiSlider.create(slider, {
    start: [0, 100], // Valores iniciales del rango
    connect: true,
    range: {
        'min': 0,
        'max': 100
    },
    step: 1 // Configurar el paso a 1 para valores enteros
});

// Obtener los valores seleccionados
slider.noUiSlider.on('update', function(values, handle) {
    var min = Math.round(values[0]);
    var max = Math.round(values[1]);
    sliderMin.textContent = min;
    sliderMax.textContent = max;
});


noUiSlider.create(slider2, {
    start: [20, 80], // Valores iniciales del rango
    connect: true,
    range: {
        'min': 0,
        'max': 100
    },
    step: 1 // Configurar el paso a 1 para valores enteros
});

// Obtener los valores seleccionados
slider2.noUiSlider.on('update', function(values, handle) {
    var min = Math.round(values[0]);
    var max = Math.round(values[1]);
    slider2Min.textContent = min;
    slider2Max.textContent = max;
});



// Set slider attributes
// var slider = document.getElementById('slider');
// var sliderMin = document.getElementById('slider-min');
// var sliderMax = document.getElementById('slider-max');

// var slider2 = document.getElementById('slider2');
// var slider2Min = document.getElementById('slider2-min');
// var slider2Max = document.getElementById('slider2-max');

// noUiSlider.create(slider, {
//   start: [minUnique, maxUnique], // Valores iniciales del rango
//   connect: true,
//   range: {
//       'min': minUnique,
//       'max': maxUnique
//   },
//   step: 1 // Configurar el paso a 1 para valores enteros
// });

// slider.on('update', function(values, handle) {
//   var min = Math.round(values[0]);
//   var max = Math.round(values[1]);
//   sliderMin.textContent = min;
//   sliderMax.textContent = max;
// });

// noUiSlider.create(slider2, {
//   start: [minCount, maxCount], // Valores iniciales del rango
//   connect: true,
//   range: {
//       'min': minCount,
//       'max': maxCount
//   },
//   step: 1 // Configurar el paso a 1 para valores enteros
// });

// slider2.on('update', function(values, handle) {
//   var min = Math.round(values[0]);
//   var max = Math.round(values[1]);
//   slider2Min.textContent = min;
//   slider2Max.textContent = max;
// });