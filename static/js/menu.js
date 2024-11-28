$(document).ready(function () {
  // Function to show the selected content section
  function showContentSection(sectionId) {
    $(".content-section").hide(); // Hide all sections
    $(sectionId).show(); // Show the selected section
  }

  // Event listeners for navigation menu
  $("#nav-market-place").on("click", function () {
    showContentSection("#market-place-content");
    $.getScript("../static/js/market_place.js");
  });

  $("#nav-seun").on("click", function () {
    showContentSection("#seun-content");
    $.getScript("../static/js/seun.js");
  });
  
  $("#nav-socio").on("click", function () {
    showContentSection("#socio-content");
    $.getScript("../static/js/socio.js");
  });

  // $("#nav-pais").on("click", function () {
  //   showContentSection("#pais-content");
  //   $.getScript("../static/js/pais.js");
  // });

  // $("#nav-oficina").on("click", function () {
  //   showContentSection("#oficina-content");
  //   $.getScript("../static/js/oficina.js");
  // });
});
