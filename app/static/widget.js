(function () {
    const script = document.currentScript;

    if (!script) {
        console.error("FlyRank widget: unable to find script element.");
        return;
    }

    const publicId = script.dataset.widget;

    if (!publicId) {
        console.error("FlyRank widget: missing data-widget attribute.");
        return;
    }

    console.log("FlyRank widget loaded:", publicId);
})();