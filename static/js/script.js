//VARIABLE PREDEFINED
let story_data = { "summary": "", "rationale": "", "story": ""};
let storySave = 1;
let timeline_data = {};
let timelineSave = 1;
let currentRowId = null;
let timelineNextId = 1;

let standardsData = {};

let isStoryTextAreaVisible = false;
let isTimelineTextAreaVisible = false;
  
//////////////////////////RELEVANT TO BOTH//////////////////////////
// text area code
document.getElementById('toggleStoryText').addEventListener('click', function() {
    const textArea = document.getElementById('storyTextArea');
    if (isStoryTextAreaVisible) {
        textArea.style.display = 'none';
        isStoryTextAreaVisible = false;
    } else {
        textArea.style.display = 'block';
        isStoryTextAreaVisible = true;
    }
});
document.getElementById('toggleTimelineText').addEventListener('click', function() {
  const textArea = document.getElementById('timelineTextArea');
  if (isTimelineTextAreaVisible) {
      textArea.style.display = 'none';
      isTimelineTextAreaVisible = false;
  } else {
      textArea.style.display = 'block';
      isTimelineTextAreaVisible = true;
  }
});


// JSON Export code
document.getElementById('saveAllJSONButton').addEventListener('click', exportAllJSON);

function exportAllJSON() {
  // Combine the two data structures
  let combinedData = {
    ...story_data,
    "timeline": Object.values(timeline_data) // Convert timeline_data from an object to an array
  };

  // Convert the combined data to a JSON string with formatting
  let jsonString = JSON.stringify(combinedData, null, 2);

  // Create a downloadable blob from the JSON string
  let blob = new Blob([jsonString], { type: "application/json" });
  let url = window.URL.createObjectURL(blob);

  // Create a download link and click it
  let a = document.createElement("a");
  a.href = url;
  a.download = "patientOutput.json";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}


//JSON import code
document.getElementById('importPatientInfo').addEventListener('change', handleFileImport);

function handleFileImport(event) {
  if (event.target.files.length > 0) {
      const file = event.target.files[0];
      const reader = new FileReader();

      reader.onload = function(e) {
          const importedData = JSON.parse(e.target.result);
          story_data.summary = importedData.summary;
          story_data.rationale = importedData.rationale;
          story_data.story = importedData.story;
          
          // Update predefined keys in story_data
          for (let key in story_data) {
            if (importedData[key]) {
                story_data[key] = importedData[key];
            }
        }
          
          // console.log("Story Data Updated:", story_data);
          updateStoryDisplay();
          updateStoryTable();


          // console.log("Story Text Area should have updated");

          // Populate timeline_data
          timeline_data = {};
          importedData.timeline.forEach((item, index) => {
            timeline_data[index] = item;
          });

          // console.log("Timeline Data Imported:", timeline_data);
          
          renderTimelineTable();
          updateTimelineDisplay(); // This function should refresh your display based on the new timeline_data
      };

      reader.onerror = function(err) {
          console.error("Error reading file:", err);
      };

      reader.readAsText(file);
  }
}



///////////////////////////STORY//////////////////////////
//story text area update

function updateStoryDisplay() {
  document.getElementById('storyTextArea').textContent = JSON.stringify(story_data, null, 2);
}

function updateStoryTable() {
  document.querySelectorAll("[data-key]").forEach(function(row) {
      const key = row.getAttribute('data-key');
      const tdElement = row.querySelector('td');
      if (!tdElement) {
          console.warn(`Skipped updating [data-key="${key}"] due to missing <td> element.`);
          return;  // skip this iteration if <td> is not found
      }
      tdElement.textContent = story_data[key] || "";
  });
}


//story story_data variable update
document.getElementById("storyTableBody").addEventListener('input', function (e) {
  // console.log("update story data")
  if (e.target && e.target.nodeName === "TD") {
      const row = e.target.closest('tr');
      const key = row.getAttribute('data-key');
      story_data[key] = e.target.textContent;
      updateStoryDisplay();
  }
});




///////////////////////////TIMELINE//////////////////////////
// timeline textarea e update
function updateTimelineDisplay() {
  document.getElementById('timelineTextArea').textContent = JSON.stringify(timeline_data, null, 2);
}

//export all code
function downloadJSON(data, filename) {
  const jsonData = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonData], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}


//timeline variable to table render code (used for import)
function renderTimelineTable() {
  let tableContent = "";
  for (let id in timeline_data) {
    const rowData = timeline_data[id];
    tableContent += `
      <tr id="row-${id}">
        <td data-key="time" contenteditable="true" class="text-left">${rowData.time}</td>
        <td data-key="event" contenteditable="true" class="text-left">${rowData.event}</td>
        <td>
          <button id="dataItemBtn-${id}" onclick="toggleDataItem(${id})">${rowData.linked_data.length > 0 ? 'Edit' : 'Add'}</button>
        </td>
        <td>
          <button class="btn btn-danger delete-row">Delete</button>
        </td>
      </tr>
    `;
  }
  document.getElementById("timelineTableBody").innerHTML = tableContent;
}


//standards dropdown populate
function populateStandardsDropdown(standards) {
  // console.log("Populating Standards: ", standards);
  const dropdown = document.getElementById('standardsDropdown');
  dropdown.innerHTML = "";
  standards.forEach((standard, index) => {
      const option = document.createElement('option');
      option.value = standard;
      option.textContent = standard;
      dropdown.appendChild(option);
  });
}

//transform main timeline for export
function transformMainTimeline(original) {
  let result = [];

  for (let key in original) {
    let item = original[key];
    let transformed = {
      time: item.time,
      event: item.event,
      sheet: item.linked_data && item.linked_data.length > 0 ? item.id.toString() : "None"
    };

    result.push(transformed);
  }

  return result;
}

// code for data path pop up
const popupWindow = document.getElementById('popupWindow');
const closePopupBtn = document.getElementById('closePopupBtn');
const popupContentText = document.getElementById('popupContentText');

let currentSelect; // This is to keep a reference to the select dropdown that triggered the popup
let editedDataPath; // This will store the edited data path from the popup

// Event delegation
document.getElementById('linked_dataTableBody').addEventListener('input', function(event) {
  if (event.target.tagName === "INPUT") {
      const selectedValue = event.target.value;

      // Check if the selected value contains at least one set of '[]'
      const regex = /\[.*?\]/;
      if (regex.test(selectedValue)) {
          // Replace every "[]" with an input field
          const modifiedValue = selectedValue.split('[]').join('[<input type="text" style="margin: 0 5px; width: 30px;">]');

          // Update the popup's content to the modified value
          popupContentText.innerHTML = modifiedValue;

          currentInput = event.target;  // Store reference to the current input box

          // Display the popup
          popupWindow.style.display = "block";
      } else {
          // Update the displayed value if it doesn't contain '[]'
          updateDisplayedValue(event.target);
      }
  }
});

// close pop up when press button
closePopupBtn.addEventListener('click', function() {
  console.log("Close button clicked")
  if (currentInput) {
    editedDataPath = currentInput.value;

    const inputElements = popupContentText.querySelectorAll('input');
    inputElements.forEach(input => {
      editedDataPath = editedDataPath.replace('[]', '[' + input.value + ']');
    });

    // Store the edited data path on the input element
    currentInput.dataset.editedDataPath = editedDataPath;

    // Update the displayed value after setting the new value to the combobox
    updateDisplayedValue(currentInput);

    currentInput = null;  // Clear reference to the input box
  }

  console.log("1.1 The edited path: " + editedDataPath)
  console.log("Current data:" + JSON.stringify(timeline_data, null, 2));
  popupWindow.style.display = "none";
});

// Close the popup when clicking outside of it
window.addEventListener('click', function(event) {
    if (event.target === popupWindow) {
      if (currentInput) {
        editedDataPath = currentInput.value;
    
        const inputElements = popupContentText.querySelectorAll('input');
        inputElements.forEach(input => {
          editedDataPath = editedDataPath.replace('[]', '[' + input.value + ']');
        });
    
        // Store the edited data path on the input element
        currentInput.dataset.editedDataPath = editedDataPath;
    
        // Update the displayed value after setting the new value to the combobox
        updateDisplayedValue(currentInput);
    
        currentInput = null;  // Clear reference to the input box
      }
  
    console.log("1.2 The edited path: " + editedDataPath)
    console.log("Current data:" + JSON.stringify(timeline_data, null, 2));
    popupWindow.style.display = "none";
      
    }
});



//timeline main DOM
document.addEventListener("DOMContentLoaded", function() {
  const linked_dataModal = document.getElementById("editModal");
  const closelinked_data = document.getElementById("closelinked_data");

  // save linked data to JSON
  function savelinked_dataToJSON() {
    const obj = timeline_data[currentRowId];
    const dropdown = document.getElementById('standardsDropdown');
    const selectedStandard = dropdown ? dropdown.value : null;
  
    obj.linked_data = [];  // Resetting linked_data to an empty array
    const rows = document.querySelectorAll("#linked_dataTableBody tr");
    rows.forEach(row => {
      const cells = row.querySelectorAll("td");
      const inputDataPath = cells[0].querySelector('input');
      const editedDataPath = inputDataPath.dataset.editedDataPath || inputDataPath.value;
  
      obj.linked_data.push({
        dataPath: editedDataPath,
        exampleData: cells[1].textContent
      });
  
      // Clear the edited data path after saving
      delete inputDataPath.dataset.editedDataPath;
    });
    
    obj.standard = selectedStandard;  // Setting the standard
  }
  

  // update timeline text area
  function updateTimelineDisplay() {
    const timelineTextAreaElem = document.getElementById("timelineTextArea");
    if (timelineTextAreaElem) {
      timelineTextAreaElem.value = JSON.stringify(timeline_data, null, 2);
    }
  }

  //render linked data modal
  function populatelinked_dataModal(rowId) {
    const obj = timeline_data[rowId];
    let tableContent = "";
    if (obj && obj.linked_data) {
      obj.linked_data.forEach((dataItem, index) => {
        let options = "";
        const paths = standardsData[obj.standard]?.dataPaths || [];
        paths.forEach(path => {
          options += `<option value="${path}">`;
        });
  
        tableContent += `
          <tr>
              <td style="width: 40%;">
                  <input list="dataPaths${index}" value="${dataItem.dataPath}" style="width: 90%;">
                  <datalist id="dataPaths${index}">
                      ${options}
                  </datalist>
              </td>
              <td contenteditable="true" class="text-left" style="width: 40%;">${dataItem.exampleData || ''}</td>
              <td style="width: 20%;">
                  <button class="btn btn-danger" onclick="deletelinked_dataRow(this, ${index})">Delete</button>
              </td>
          </tr>
        `;
      });
    }
    document.getElementById("linked_dataTableBody").innerHTML = tableContent;
  }
  
  // add row to linked data modal
  window.addlinked_dataRow = function() {
    const selectedStandard = document.getElementById('standardsDropdown').value;
    const defaultPaths = standardsData[selectedStandard]?.dataPaths || [];
    let options = "";
    defaultPaths.forEach(path => {
      options += `<option value="${path}">`;
    });
  
    const currentRowCount = document.querySelectorAll('#linked_dataTableBody tr').length;
  
    const newRow = document.createElement('tr');
    newRow.innerHTML = `
          <td style="width: 40%;">
              <input list="dataPaths${currentRowCount}" style="width: 90%;">
              <datalist id="dataPaths${currentRowCount}">
                  ${options}
              </datalist>
          </td>
          <td contenteditable="true" class="text-left" style="width: 40%;"></td>
          <td style="width: 20%;">
              <button class="btn btn-danger" onclick="deletelinked_dataRow(this)">Delete</button>
          </td>
      `;
    document.getElementById("linked_dataTableBody").appendChild(newRow);
};

  // delete row from timeline json
  window.deleteRow = function(rowId) {
    delete timeline_data[rowId];
    const rowElement = document.getElementById("row-" + rowId);
    if (rowElement) {
      rowElement.remove();
    }
    updateTimelineDisplay();
  }

  // reset linked data when deleted
  window.resetlinked_data = function() {
    const obj = timeline_data[currentRowId];
    if (obj) {
      obj.linked_data = [];
      delete obj.standard;
    }
    const btn = document.getElementById("dataItemBtn-" + currentRowId);
    if (btn) {
      btn.innerText = "Add";
    }
    linked_dataModal.style.display = "none";
    updateTimelineDisplay();
  }

  // switch between Add and Edit for row
  window.toggleDataItem = function(rowId) {
    const btn = document.getElementById("dataItemBtn-" + rowId);
    if (btn.innerText === "Add" || btn.innerText === "Edit") {
      btn.innerText = "Edit";
      currentRowId = rowId;
      linked_dataModal.style.display = "block"; 
      populatelinked_dataModal(rowId);
    } else {
      btn.innerText = "Add";
      currentRowId = null;
    }
  }

  // delete row from pop up table
  window.deletelinked_dataRow = function(buttonElem, index) {
    buttonElem.parentElement.parentElement.remove();
    timeline_data[currentRowId].linked_data.splice(index, 1);  // Remove the corresponding object from linked_data
    savelinked_dataToJSON();
    updateTimelineDisplay();
  }

//  update combobox when user changes it
  window.updateDisplayedValue = function(inputElem) {
    const displayedDataPathElem = inputElem.parentElement.querySelector('.displayed-data-path');
    if (displayedDataPathElem) {
        displayedDataPathElem.textContent = inputElem.value;
    }
}

  // close pop up table
  closelinked_data.onclick = function() {
    linked_dataModal.style.display = "none";
    savelinked_dataToJSON();
    updateTimelineDisplay();
  }
  
  // close pop up table when clicked outside
  linked_dataModal.addEventListener("click", function(event) {
    if (event.target === linked_dataModal) {
      savelinked_dataToJSON();
      updateTimelineDisplay();
      linked_dataModal.style.display = "none";
    }
  });

  //add blank row to timeline
  document.getElementById("addBlankRowBtn").addEventListener("click", function() {
    console.log("Adding blank timeline row")

    timeline_data[timelineNextId] = {
      time: "",
      event: "",
      standard: null,
      linked_data: []
    };
    
    const newRow = `
      <tr id="row-${timelineNextId}">
        <td data-key="time" contenteditable="true" class="text-left"></td>
        <td data-key="event" contenteditable="true" class="text-left"></td>
        <td>
          <button id="dataItemBtn-${timelineNextId}" onclick="toggleDataItem(${timelineNextId})">Add</button>
        </td>
        <td>
          <button class="btn btn-danger delete-row">Delete</button>
        </td>
      </tr>
    `;
  
    document.getElementById("timelineTableBody").innerHTML += newRow;
    timelineNextId++;
    updateTimelineDisplay();
  });

  // standards file import
  document.getElementById('standardsFileLoadButton').addEventListener('change', function(e) {
  
    console.log("File change event triggered");
    const files = e.target.files;
    if (!files.length) return;
    console.log("Number of files: " + files.length)
    console.log("Name of files (in import): " + files)
    
    Array.from(files).forEach((file, fileIndex) => {
      const reader = new FileReader();
      reader.onload = function(e) {
          const contents = JSON.parse(e.target.result);
          // console.log("File Contents:", contents);

          // Using file name as standard name (removing .json extension)
          const standardName = file.name.replace('.json', '');
          console.log(standardName)

          if(standardName) {
              standardsData[standardName] = {
                  dataPaths: contents.filter(Boolean) // Remove any falsy values from the data paths (like empty strings)
              };
          }

          console.log(Object.keys(standardsData));

          populateStandardsDropdown(Object.keys(standardsData));
          
      };
      reader.readAsText(file); // We still read as text but then parse the result as JSON
    });  
});

// delete timeline table row
  document.getElementById("timelineTableBody").addEventListener("click", function(event) {
    if (event.target && event.target.matches(".delete-row")) {
      const rowElement = event.target.closest("tr");
      if (rowElement && rowElement.id) {
        const rowId = parseInt(rowElement.id.split("-")[1]);
        delete timeline_data[rowId];
        rowElement.remove();
        updateTimelineDisplay();
      }
    }
  });
  
  // update timeline json + text area when value changes
  document.getElementById("timelineTableBody").addEventListener("input", function(event) {
    const cell = event.target.closest("td");
    if (cell && cell.hasAttribute("data-key")) {
      const key = cell.getAttribute("data-key");
      const rowElement = cell.closest("tr");
      if (rowElement && rowElement.id) {
        const rowId = parseInt(rowElement.id.split("-")[1]);
        timeline_data[rowId][key] = cell.textContent;
        updateTimelineDisplay();
      }
    }
  });

  // when linked_datatable is no longer a fous, update JSON and timeline display
  document.getElementById("linked_dataTableBody").addEventListener("blur", function(event) {
    savelinked_dataToJSON();
    updateTimelineDisplay();
  }, true);

  // update pop up table when standard changes IDK
  document.getElementById("linked_dataTableBody").addEventListener("change", function(event) {
    if (event.target && event.target.matches(".standard-dropdown")) {
      savelinked_dataToJSON();
      updateTimelineDisplay();
    }
  }, true);

  // update pop up table when standard changes
  document.getElementById('standardsDropdown').addEventListener('change', function(event) {
    const selectedStandard = event.target.value;
    const paths = standardsData[selectedStandard]?.dataPaths || [];
    console.log("Selected Standard:", selectedStandard);
  
    document.querySelectorAll('#linked_dataTableBody tr').forEach((row, index) => {
      const input = row.querySelector('input');
      const dataListId = input.getAttribute('list');
      const dataList = document.getElementById(dataListId);
  
      if (dataList) {
        dataList.innerHTML = paths.map(path => `<option value="${path}">${path}</option>`).join('');
      }
    });
  
    savelinked_dataToJSON();
    updateTimelineDisplay();
  });

});