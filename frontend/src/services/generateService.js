export async function handleGenerate(selectedTracks, prompt, { onError, onSuccess, onLoading }) {
  if (selectedTracks.length === 0) {
    onError("No tracks selected. Please upload a track first.");
    return;
  }

  for (const track of selectedTracks) {
    if (!track.file) {
      onError(`"${track.name}" is not an uploaded file. Please upload an audio file to use Generate.`);
      return;
    }
  }

  const formData = new FormData();
  formData.append("file1", selectedTracks[0].file);
  formData.append("stem1", selectedTracks[0].stem);

  if (selectedTracks.length >= 2) {
    formData.append("file2", selectedTracks[1].file);
    formData.append("stem2", selectedTracks[1].stem);
  }

  formData.append("prompt", prompt);

  onLoading(true);
  onError(null);

  try {
    const response = await fetch("/api/upload_file", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Server returned ${response.status}: ${response.statusText}`);
    }

    const { url } = await response.json();
    const fileResponse = await fetch(`/api${url}`);

    if (!fileResponse.ok) {
      throw new Error("Failed to fetch generated file.");
    }

    const blob = await fileResponse.blob();
    const audioUrl = URL.createObjectURL(blob);
    const filename = `${selectedTracks[0].name.replace(/\.[^/.]+$/, "")}_generated.wav`;

    onSuccess(audioUrl, filename);
  } catch (err) {
    onError(`Generation failed: ${err.message}`);
  } finally {
    onLoading(false);
  }
}