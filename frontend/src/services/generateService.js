// const BACKEND_URL = "http://127.0.0.1:5000";
const BACKEND_URL = "";

/*
  handleGenerate
  - selectedTracks: array of { name, stem, file? }
  - onError: (message: string) => void
  - onSuccess: (audioUrl: string, filename: string) => void
  - onLoading: (isLoading: bool) => void
*/
export async function handleGenerate(selectedTracks, prompt, { onError, onSuccess, onLoading }) {
  // validation
  if (selectedTracks.length === 0) {
    onError("No tracks selected. Please upload or select a track first.");
    return;
  }

  const track = selectedTracks[0];
  console.log("Track:", track);

  if (!track.file) {
    onError(`"${track.name}" is a search result, not an uploaded file. Please upload an audio file to use Generate.`);
    return;
  }

  // build request
  const formData = new FormData();
  const track1 = selectedTracks[0];
  formData.append("file1", track1.file);
  formData.append("stem1", track1.stem);

  if (selectedTracks.length === 2) {
    const track2 = selectedTracks[1];
    formData.append("file2", track2.file);
    formData.append("stem2", track2.stem);
  }

  formData.append("prompt", prompt);

  onLoading(true);
  onError(null);

  try {
    // POST to upload and split
    console.log("Step 1: sending POST...");
    const response = await fetch(`/api/upload_file`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Server returned ${response.status}: ${response.statusText}`);
    }

    // Flask returns { url: "http://127.0.0.1:5000/stems/<filename>" }
    console.log("Step 2: POST response status:", response.status);
    const data = await response.json();
    console.log("Step 3: got JSON:", data);

    // fetch the actual audio file from the returned URL
    // const fileResponse = await fetch(data.url);
    const fileResponse = await fetch(`/api${data.url}`);
    console.log("Step 4: file fetch status:", fileResponse.status);

    if (!fileResponse.ok) {
      throw new Error("Failed to fetch stem file.");
    }

    const blob = await fileResponse.blob();
    const audioUrl = URL.createObjectURL(blob);
    const baseName = track.name.replace(/\.[^/.]+$/, "");
    const filename = `${baseName}_${track.stem}.wav`;

    onSuccess(audioUrl, filename);
  } catch (err) {
    onError(`Generation failed: ${err.message}`);
  } finally {
    onLoading(false);
  }
}