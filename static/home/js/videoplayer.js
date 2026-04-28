document.addEventListener('DOMContentLoaded', function () {
  const video       = document.getElementById('mainVideo');
  const sourceEl    = document.getElementById('mainVideoSource');
  const titleEl     = document.getElementById('videoTitle');
  const list        = document.getElementById('videoPlaylist');

  const shareFacebook  = document.getElementById('shareFacebook');
  const shareX         = document.getElementById('shareX');
  const shareReddit    = document.getElementById('shareReddit');
  const copyLinkBtn    = document.getElementById('copyLinkBtn');
  const nativeShareBtn = document.getElementById('nativeShareBtn');

  if (!video || !list) return;

  const items = Array.from(list.querySelectorAll('li.video-item'));
  if (!items.length) return;

  let currentIndex = items.findIndex(li => li.classList.contains('active'));
  if (currentIndex < 0) currentIndex = 0;

  let currentTitle = items[currentIndex].dataset.title || 'Video';
  let currentUrl   = window.location.href;

  function formatTime(seconds) {
    if (!isFinite(seconds)) return '';
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  }

  function updateShareLinks(pageUrl, title, durationText) {
    currentUrl   = pageUrl;
    currentTitle = title;

    const niceTitle   = title || 'Video';
    const extra       = durationText ? ` (${durationText})` : '';
    const tweetText   = `Check this out: ${niceTitle}${extra}`;
    const redditTitle = `${niceTitle}${extra}`;

    if (shareFacebook) {
      shareFacebook.href =
        'https://www.facebook.com/sharer/sharer.php?u=' +
        encodeURIComponent(pageUrl);
    }
    if (shareX) {
      shareX.href =
        'https://twitter.com/intent/tweet?url=' +
        encodeURIComponent(pageUrl) +
        '&text=' + encodeURIComponent(tweetText);
    }
    if (shareReddit) {
      shareReddit.href =
        'https://www.reddit.com/submit?url=' +
        encodeURIComponent(pageUrl) +
        '&title=' + encodeURIComponent(redditTitle);
    }
  }

  function loadFromItem(index, pushUrl = true) {
    const item = items[index];
    if (!item) return;

    const src   = item.dataset.src;
    const title = item.dataset.title || 'Video';
    const url   = item.dataset.url; // /music/videos/?v=...

    if (sourceEl) {
      sourceEl.src = src;
    } else {
      video.src = src;
    }

    video.load();
    video.play().catch(() => {});

    if (titleEl) {
      titleEl.textContent = title;
      // Also update page title
      document.title = title + ' - Videos | Lab Munkz Ink';
    }

    items.forEach(li => li.classList.remove('active'));
    item.classList.add('active');

    let newUrl = window.location.href;
    if (pushUrl && url) {
      newUrl = new URL(url, window.location.origin).toString();
      window.history.pushState({}, '', newUrl);
    }

    // We'll refine with real duration when metadata loads
    updateShareLinks(newUrl, title, '');
  }

  // Click on playlist
  list.addEventListener('click', function (e) {
    const li = e.target.closest('li.video-item');
    if (!li) return;

    e.preventDefault();

    const index = items.indexOf(li);
    if (index === -1) return;

    currentIndex = index;
    loadFromItem(index);
  });

  // Auto-next on end
  video.addEventListener('ended', function () {
    currentIndex = (currentIndex + 1) % items.length;
    loadFromItem(currentIndex);
  });

  // When current video metadata loads, update share text with duration
  video.addEventListener('loadedmetadata', function () {
    const durText = formatTime(video.duration);
    updateShareLinks(currentUrl, currentTitle, durText);
  });

  // Fill durations on playlist entries using hidden video elements
  items.forEach(item => {
    const durationEl = item.querySelector('.track-duration');
    if (!durationEl) return;

    const src = item.dataset.src;
    if (!src) return;

    const temp = document.createElement('video');
    temp.preload = 'metadata';
    temp.src = src;

    temp.addEventListener('loadedmetadata', function () {
      const durText = formatTime(temp.duration);
      durationEl.textContent = durText || '--:--';
      temp.remove();
    });

    temp.addEventListener('error', function () {
      durationEl.textContent = '--:--';
      temp.remove();
    });
  });

  // Copy Link
  if (copyLinkBtn) {
    copyLinkBtn.addEventListener('click', function () {
      if (!navigator.clipboard) {
        alert('Clipboard not supported.');
        return;
      }
      navigator.clipboard.writeText(currentUrl)
        .then(() => alert('Link copied!'))
        .catch(() => alert('Could not copy link.'));
    });
  }

  // Native share (mobile, etc.)
  if (nativeShareBtn) {
    nativeShareBtn.addEventListener('click', function () {
      if (!navigator.share) {
        alert("Your browser doesn't support native sharing.");
        return;
      }
      const durText = formatTime(video.duration);
      const text = `Check this out: ${currentTitle}${durText ? ' (' + durText + ')' : ''}`;
      navigator.share({
        title: currentTitle,
        text: text,
        url: currentUrl,
      }).catch(() => {});
    });
  }

  // Initial share setup
  const initialTitle = titleEl ? titleEl.textContent : currentTitle;
  updateShareLinks(window.location.href, initialTitle, '');
});
