$(document).ready(function () {
  // Fetch DataFrame from FastAPI
  function fetchDataFrame() {
    $.getJSON("/dataframe", function (data) {
      generateTable(data);
    });
  }

  // Fetch DataFrame range from FastAPI
  function fetchDataFrameRange() {
    $.getJSON("/dataframe_range", function (data) {
      $("#valueSliderUnique").attr("min", data.min_unique);
      $("#valueSliderUnique").attr("max", data.max_unique);
      $("#valueSliderUnique").val(data.min_unique);
      $("#sliderValueUnique").text(data.min_unique);

      $("#valueSliderCount").attr("min", data.min_count);
      $("#valueSliderCount").attr("max", data.max_count);
      $("#valueSliderCount").val(data.min_count);
      $("#sliderValueCount").text(data.min_count);
    });
  }

  // Function to generate table
  function generateTable(data) {
    let tableContent = `
      <thead>
        <tr>
          <th class="px-4 py-2">SEUN/Líder País</th>
          <th class="px-4 py-2">Mes</th>
          <th class="px-4 py-2">No_Personal_Unique</th>
          <th class="px-4 py-2">No_Personal_Count</th>
          <th class="px-4 py-2">e-mail</th>
        </tr>
      </thead>
      <tbody>
    `;
    data.forEach((row) => {
      tableContent += `
        <tr>
          <td class="border px-4 py-2">${row["SEUN/Líder País"]}</td>
          <td class="border px-4 py-2">${row["Mes"]}</td>
          <td class="border px-4 py-2">${row["No_Personal_Unique"]}</td>
          <td class="border px-4 py-2">${row["No_Personal_Count"]}</td>
          <td class="border px-4 py-2">${row["e-mail"]}</td>
        </tr>
      `;
    });
    tableContent += "</tbody>";
    $("#dataTable").html(tableContent);
  }

  // Initial table generation
  fetchDataFrame();
  fetchDataFrameRange();

  // Update slider value display
  $("#valueSliderUnique").on("input", function () {
    $("#sliderValueUnique").text($(this).val());
  });

  $("#valueSliderCount").on("input", function () {
    $("#sliderValueCount").text($(this).val());
  });

  // Filter table based on slider values and selected month
  function filterTable() {
    const filterValueUnique = $("#valueSliderUnique").val();
    const filterValueCount = $("#valueSliderCount").val();
    const selectedMonth = $("#monthSelect").val();
    $.getJSON("/dataframe", function (data) {
      const filteredData = data.filter(
        (row) =>
          row["No_Personal_Unique"] >= filterValueUnique &&
          row["No_Personal_Count"] >= filterValueCount &&
          (selectedMonth === "all" || row["Mes"] == selectedMonth)
      );
      generateTable(filteredData);
    });
  }

  $("#valueSliderUnique").on("change", filterTable);
  $("#valueSliderCount").on("change", filterTable);
  $("#monthSelect").on("change", filterTable);

  // Send email function
  $("#sendEmailButton").on("click", function () {
    const sliderValueUnique = $("#valueSliderUnique").val();
    const sliderValueCount = $("#valueSliderCount").val();
    const selectedMonth = $("#monthSelect").val();

    // Show loading spinner
    $("#loadingSpinner").removeClass("hidden");

    $.post(
      "/send_email",
      {
        slider_value_unique: sliderValueUnique,
        slider_value_count: sliderValueCount,
        selected_month: selectedMonth,
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
