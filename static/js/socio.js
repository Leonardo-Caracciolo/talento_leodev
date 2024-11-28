$(document).ready(function () {
  console.log("Hola desde Socio");

  // Define the HTML content for SEUN
  const socioContent = `
    <div class="flex flex-col gap-4">
      <!-- Filtros Card -->
      <div class="bg-white shadow-md rounded-lg p-6">
        <h2 class="text-xl font-semibold mb-4">Filtros</h2>
        <div class="mb-4">
          <label for="valueSliderUnique" class="block text-gray-700">Cantidad de personal mensual (Unique):</label>
          <input type="range" id="valueSliderUnique" class="w-full" />
          <span id="sliderValueUnique" class="block text-gray-700 mt-2"></span>
        </div>
        <div class="mb-4">
          <label for="valueSliderCount" class="block text-gray-700">Cantidad de personal mensual (Count):</label>
          <input type="range" id="valueSliderCount" class="w-full" />
          <span id="sliderValueCount" class="block text-gray-700 mt-2"></span>
        </div>
        <div class="mb-4">
          <label for="monthSelect" class="block text-gray-700">Mes:</label>
          <select id="monthSelect" class="w-full border border-gray-300 rounded-lg p-2">
            <option value="all">Todos</option>
          </select>
        </div>
        <div class="mb-4">
          <label for="serviceLineSelect" class="block text-gray-700">Pais:</label>
          <select id="serviceLineSelect" class="w-full border border-gray-300 rounded-lg p-2">
            <option value="all">Todos</option>
          </select>
        </div>
        <div class="mb-4">
          <label for="countrySelect" class="block text-gray-700">Pais:</label>
          <select id="countrySelect" class="w-full border border-gray-300 rounded-lg p-2">
            <option value="all">Todos</option>
          </select>
        </div>
        <div class="mb-4">
          <label for="officeSelect" class="block text-gray-700">Pais:</label>
          <select id="officeSelect" class="w-full border border-gray-300 rounded-lg p-2">
            <option value="all">Todos</option>
          </select>
        </div>
        <button id="sendEmailButton" class="bg-blue-500 text-white px-4 py-2 rounded mt-4 w-full">Send Email</button>
      </div>

      <!-- Tabla Card -->
      <div class="bg-white shadow-md rounded-lg p-6">
        <h2 class="text-xl font-semibold mb-4">Datos</h2>
        <table id="dataTable" class="min-w-full bg-white">
          <!-- Table content will be generated by JavaScript -->
        </table>
      </div>
    </div>
  `;

  // Inject the HTML content into the #socio-content container
  $("#socio-content").html(socioContent);

  // Sliders
  var slider = document.getElementById('slider');
  var slider2 = document.getElementById('slider2');

  // Socio related scripts
  function fetchDataFrame(endpoint) {
    $.getJSON(endpoint, function (data) {
      // Calculate min and max values for sliders
      const minUnique = Math.min(
        ...data.map((row) => row.profesionales_no_entregaron)
      );
      const maxUnique = Math.max(
        ...data.map((row) => row.profesionales_no_entregaron)
      );
      const minCount = Math.min(
        ...data.map((row) => row.reportes_no_entregados)
      );
      const maxCount = Math.max(
        ...data.map((row) => row.reportes_no_entregados)
      );
      const uniqueMonths = [...new Set(data.map((row) => row.Mes))].sort(
        (a, b) => a - b
      );
      const uniqueServicelines = [...new Set(data.map((row) => row.Linea))];
      const uniqueCountries = [...new Set(data.map((row) => row.Pais))];
      const uniqueOffices = [...new Set(data.map((row) => row.Oficina))];

      // Set slider attributes
      slider.noUiSlider.updateOptions({
        start: [minUnique, maxUnique], // Valores iniciales del rango
        range: {
            'min': minUnique,
            'max': maxUnique
        }
      });
      $("#slider-min").text(minUnique);
      $("#slider-max").text(maxUnique);
      
      slider2.noUiSlider.updateOptions({
        start: [minCount, maxCount], // Valores iniciales del rango
        range: {
            'min': minCount,
            'max': maxCount
        }
      });
      $("#slider2-min").text(minCount);
      $("#slider2-max").text(maxCount);

      // Populate month select options
      let monthOptions = '<option value="all">All</option>';
      uniqueMonths.forEach((month) => {
        monthOptions += `<option value="${month}">${month}</option>`;
      });
      $("#monthSelect").html(monthOptions);
      
      // Populate serviceline select options
      let servicelineOptions = '<option value="all">All</option>';
      uniqueServicelines.forEach((serviceline) => {
        servicelineOptions += `<option value="${serviceline}">${serviceline}</option>`;
      });
      $("#serviceLineSelect").html(servicelineOptions);

      // Populate country select options
      let countryOptions = '<option value="all">All</option>';
      uniqueCountries.forEach((country) => {
        countryOptions += `<option value="${country}">${country}</option>`;
      });
      $("#countrySelect").html(countryOptions);

      // Populate office select options
      let officeOptions = '<option value="all">All</option>';
      uniqueOffices.forEach((office) => {
        officeOptions += `<option value="${office}">${office}</option>`;
      });
      $("#officeSelect").html(officeOptions);

      // Generate table with data
      generateTable(data);
    });
  }

  // Function to generate table
  function generateTable(data) {
    let tableContent = `
      <thead>
        <tr>
          <th class="px-4 py-2">Mes</th>
          <th class="px-4 py-2">SAP</th>
          <th class="px-4 py-2">Socio</th>
          <th class="px-4 py-2">Línea de Servicio</th>
          <th class="px-4 py-2">Pais</th>
          <th class="px-4 py-2">Oficina</th>
          <th class="px-4 py-2">Reportes no entregados</th>
          <th class="px-4 py-2">Profesionales que no entregaron reportes</th>
          <th class="px-4 py-2">Tiene Grupo Asignado</th>
        </tr>
      </thead>
      <tbody>
    `;
    data.forEach((row) => {
      tableContent += `
        <tr>
          <td class="border px-4 py-2">${row.Mes}</td>
          <td class="border px-4 py-2">${row.SAP_Socio}</td>
          <td class="border px-4 py-2">${row.Socio}</td>
          <td class="border px-4 py-2">${row.Linea}</td>
          <td class="border px-4 py-2">${row.Pais}</td>
          <td class="border px-4 py-2">${row.Oficina}</td>
          <td class="border px-4 py-2">${row.reportes_no_entregados}</td>
          <td class="border px-4 py-2">${row.profesionales_no_entregaron}</td>
          <td class="border px-4 py-2">${row.Tiene_Grupo_Asignado}</td>
        </tr>
      `;
    });
    tableContent += "</tbody>";
    $("#dataTable").html(tableContent);
  }

  // Initial table generation
  fetchDataFrame("/aggregated_socio_data_resumen/");

  // Filter table based on slider values and selected month
  function filterTable() {
    var filterValueCountMin = parseInt($("#slider2-min").text());
    var filterValueCountMax = parseInt($("#slider2-max").text());
    var filterValueUniqueMin = parseInt($("#slider-min").text());
    var filterValueUniqueMax = parseInt($("#slider-max").text());
    const selectedMonth = $("#monthSelect").val();
    const selectedServiceline = $("#serviceLineSelect").val();
    const selectedCountry = $("#countrySelect").val();
    const selectedOffice = $("#officeSelect").val();
    $.getJSON("/aggregated_socio_data_resumen/", function (data) {
      const filteredData = data.filter(
        (row) =>
          row.profesionales_no_entregaron >= filterValueUniqueMin &&
          row.profesionales_no_entregaron <= filterValueUniqueMax &&
          row.reportes_no_entregados >= filterValueCountMin &&
          row.reportes_no_entregados <= filterValueCountMax &&
          (selectedMonth === "all" || row.Mes == selectedMonth) &&
          (selectedServiceline === "all" || row.Linea == selectedServiceline) &&
          (selectedCountry === "all" || row.Pais == selectedCountry) &&
          (selectedOffice === "all" || row.Oficina == selectedOffice)
      );
      generateTable(filteredData);
    });
  }

  // Update filters
  slider.noUiSlider.on("update", filterTable);
  slider2.noUiSlider.on("update", filterTable);
  $("#monthSelect").on("change", filterTable);
  $("#serviceLineSelect").on("change", filterTable);
  $("#countrySelect").on("change", filterTable);
  $("#officeSelect").on("change", filterTable);

  // Send email function
  $("#sendEmailButton").on("click", function () {
    const sliderValueUnique = $("#valueSliderUnique").val();
    const sliderValueCount = $("#valueSliderCount").val();
    const selectedMonth = $("#monthSelect").val();
    const selectedCountry = $("#countrySelect").val();
    const selectedOffice = $("#officeSelect").val();
    const selectedLine = $("#lineSelect").val();

    // Show loading spinner
    $("#loadingSpinner").removeClass("hidden");

    $.post(
      "/send_email_socio",
      {
        slider_value_unique: sliderValueUnique,
        slider_value_count: sliderValueCount,
        selected_country: selectedCountry,
        selected_office: selectedOffice,
        selected_line: selectedLine,
      },
      function (response) {
        alert(response.message);
        // Hide loading spinner
        $("#loadingSpinner").addClass("hidden");
      }
    ).fail(function () {
      alert("Error sending email.");
      // Hide loading spinner
      $("#loadingSpinner").addClass("hidden");
    });
  });
});
