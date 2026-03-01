document.addEventListener("DOMContentLoaded", function () {

    const tableBody = document.querySelector("#products-table tbody");
    const addBtn = document.getElementById("add-row");

    /* ================================
       CALCULATE SINGLE ROW
    ================================== */
    function calculateRow(row) {
        const qty = parseFloat(row.querySelector(".qty").value) || 0;
        const price = parseFloat(row.querySelector(".price").value) || 0;
        const totalField = row.querySelector(".total");

        totalField.value = (qty * price).toFixed(2);
        calculateSummary();
    }

    /* ================================
       CALCULATE SUMMARY
    ================================== */
    function calculateSummary() {
        let subtotal = 0;

        document.querySelectorAll(".total").forEach(function (input) {
            subtotal += parseFloat(input.value) || 0;
        });

        let cgst = subtotal * 0.09;
        let sgst = subtotal * 0.09;
        let grandTotal = subtotal + cgst + sgst;

        // Update UI
        document.getElementById("subtotal").innerText = subtotal.toFixed(2);
        document.getElementById("cgst").innerText = cgst.toFixed(2);
        document.getElementById("sgst").innerText = sgst.toFixed(2);
        document.getElementById("grandtotal").innerText = grandTotal.toFixed(2);

        // ✅ Update hidden fields for backend
        const subtotalInput = document.getElementById("subtotal_input");
        const cgstInput = document.getElementById("cgst_input");
        const sgstInput = document.getElementById("sgst_input");
        const grandInput = document.getElementById("grandtotal_input");

        if (subtotalInput) subtotalInput.value = subtotal.toFixed(2);
        if (cgstInput) cgstInput.value = cgst.toFixed(2);
        if (sgstInput) sgstInput.value = sgst.toFixed(2);
        if (grandInput) grandInput.value = grandTotal.toFixed(2);
    }

    /* ================================
       ADD NEW PRODUCT ROW
    ================================== */
    addBtn.addEventListener("click", function () {
        const rowCount = tableBody.rows.length + 1;

        const newRow = document.createElement("tr");
        newRow.innerHTML = `
            <td>${rowCount}</td>
            <td><input type="text" name="product_name[]" required></td>
            <td><input type="number" name="quantity[]" class="qty" value="1" min="1" required></td>
            <td><input type="number" name="price[]" class="price" value="0" min="0" step="0.01" required></td>
            <td><input type="number" name="total[]" class="total" value="0.00" readonly></td>
            <td><button type="button" class="remove-row">X</button></td>
        `;

        tableBody.appendChild(newRow);
    });

    /* ================================
       DETECT INPUT CHANGES
    ================================== */
    tableBody.addEventListener("input", function (e) {
        if (e.target.classList.contains("qty") || 
            e.target.classList.contains("price")) {

            const row = e.target.closest("tr");
            calculateRow(row);
        }
    });

    /* ================================
       REMOVE ROW
    ================================== */
    tableBody.addEventListener("click", function (e) {
        if (e.target.classList.contains("remove-row")) {
            e.target.closest("tr").remove();
            updateRowNumbers();
            calculateSummary();
        }
    });

    /* ================================
       UPDATE ROW NUMBERS
    ================================== */
    function updateRowNumbers() {
        Array.from(tableBody.rows).forEach((row, index) => {
            row.cells[0].innerText = index + 1;
        });
    }

    /* ================================
       INITIAL CALCULATION ON LOAD
    ================================== */
    document.querySelectorAll("#products-table tbody tr").forEach(function (row) {
        calculateRow(row);
    });

});

