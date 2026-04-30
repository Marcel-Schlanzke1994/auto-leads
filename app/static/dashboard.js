(function () {
  const filterInput = document.getElementById("lead-filter");
  const leadTable = document.getElementById("lead-table");

  if (filterInput && leadTable) {
    const rows = Array.from(leadTable.querySelectorAll("tbody tr"));
    filterInput.addEventListener("input", () => {
      const value = filterInput.value.trim().toLowerCase();
      rows.forEach((row) => {
        const text = row.textContent.toLowerCase();
        row.style.display = !value || text.includes(value) ? "" : "none";
      });
    });
  }

  const jobPanel = document.getElementById("job-panel");
  if (!jobPanel) {
    return;
  }

  const jobId = Number.parseInt(jobPanel.dataset.jobId || "", 10);
  const initialStatus = (jobPanel.dataset.jobStatus || "").toLowerCase();
  if (!jobId || ["finished", "failed"].includes(initialStatus)) {
    return;
  }

  const statusNode = document.getElementById("job-status");
  const messageNode = document.getElementById("job-message");
  const metaNode = document.getElementById("job-meta");
  const barNode = document.getElementById("job-progress-bar");

  const refresh = async () => {
    try {
      const response = await fetch(`/api/search/progress?job_id=${jobId}`);
      if (!response.ok) {
        return;
      }
      const data = await response.json();
      if (statusNode) {
        statusNode.textContent = data.status || "unknown";
        statusNode.className = `pill ${data.status || ""}`;
      }
      if (messageNode) {
        messageNode.textContent = data.message || "";
      }

      const targetCount = data.target_count || 0;
      const created = data.total_created || 0;
      const progress =
        targetCount > 0 ? Math.min(100, Math.round((created / targetCount) * 100)) : 0;
      if (barNode) {
        barNode.style.width = `${progress}%`;
      }
      if (metaNode) {
        metaNode.textContent =
          `Ziel ${created} / ${targetCount} neue Leads · Roh ${data.total_found_raw || 0} · ` +
          `Verarbeitet ${data.total_processed || 0} · Dubletten ${data.duplicates_skipped || 0} · ` +
          `Gefiltert ${data.filtered_out || 0} · Fehler ${data.errors || 0} · ` +
          `Stadt ${data.current_city || "-"} · Query ${data.current_query || "-"}`;
      }

      if (["finished", "failed"].includes((data.status || "").toLowerCase())) {
        window.clearInterval(intervalId);
      }
    } catch (error) {
      window.clearInterval(intervalId);
    }
  };

  const intervalId = window.setInterval(refresh, 2500);
})();
