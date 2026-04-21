// const BACKEND_URL = "http://127.0.0.1:5000";
const BACKEND_URL = "";

/*
  handleGenerate
  - selectedTracks: array of { name, stem, file? }
  - onError: (message: string) => void
  - onSuccess: (audioUrl: string, filename: string) => void
  - onLoading: (isLoading: bool) => void
*/
export async function handleGenerate(selectedTracks, { onError, onSuccess, onLoading }) {
  // validation
  if (selectedTracks.length === 0) {
    onError("No tracks selected. Please upload or select a track first.");
    return;
  }

  const hasUploadedFile = selectedTracks.some(track => track.file);
  if (!hasUploadedFile) {
    onError("All selected tracks are search results. Please upload at least one audio file to use Generate.");
    return;
  }

  // build request — append each track as "files" / "stems" so the backend
  // receives parallel lists regardless of how many tracks are selected
  const formData = new FormData();
  for (const track of selectedTracks) {
    if (!track.file) continue; // skip search results
    formData.append("files", track.file);
    formData.append("stems", track.stem);
  }

  onLoading(true);
  onError(null);

  try {
    console.log("Step 1: sending POST...");
    const response = await fetch(`/api/upload_file`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `Server returned ${response.status}: ${response.statusText}`);
    }

    console.log("Step 2: POST response status:", response.status);
    const data = await response.json();
    console.log("Step 3: got JSON:", data);

    const fileResponse = await fetch(`/api${data.url}`);
    console.log("Step 4: file fetch status:", fileResponse.status);

    if (!fileResponse.ok) {
      throw new Error("Failed to fetch generated file.");
    }

    const blob = await fileResponse.blob();
    const audioUrl = URL.createObjectURL(blob);

    // build a filename from all selected track names and stems
    const label = selectedTracks
      .filter(t => t.file)
      .map(t => `${t.name.replace(/\.[^/.]+$/, "")}_${t.stem}`)
      .join("+");
    const filename = `${label}.wav`;

    onSuccess(audioUrl, filename);
  } catch (err) {
    onError(`Generation failed: ${err.message}`);
  } finally {
    onLoading(false);
  }
}