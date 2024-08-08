function highlightSelection() {
  let selection = window.getSelection();
  if (selection.rangeCount > 0) {
    let range = selection.getRangeAt(0);
    let selectedText = range.toString().trim();

    if (selectedText.length > 0) {
      let span = document.createElement('span');
      span.style.backgroundColor = 'yellow';
      span.textContent = `*${selectedText}*`;

      range.deleteContents();
      range.insertNode(span);

      selection.removeAllRanges();
    }
  }
}

document.addEventListener('mouseup', highlightSelection);