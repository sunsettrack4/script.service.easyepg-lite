
const blockPage = document.getElementById("page-blocker");

const chInSetup = document.getElementsByClassName("channels-in-setup");
const noChInSetup = document.getElementById("no-channels-in-setup");
const searchResultsText = document.getElementById("search-results-text");

const chSearchBar = document.getElementById("channel-search");
const lpSearchBar = document.getElementById("lineup-channel-search");

const chSelectAll = document.getElementById("ch-select-all");
const chUnselectAll = document.getElementById("ch-unselect-all");
const chRemoveAll = document.getElementById("ch-remove-all");
const chMap = document.getElementById("ch-map");

const chLpSelectAll = document.getElementById("ch-lp-select-all");
const chLpUnselectAll = document.getElementById("ch-lp-unselect-all");
const chLpAddAll = document.getElementById("ch-lp-add-all");

const chRemove = document.getElementById("ch-remove");

const mainBtnGroup = document.getElementById("btn-main-group");
const aboutBtnGroup = document.getElementById("about-btn-group");
const chMultiSelectBtnGroup = document.getElementById("btn-ch-select-group");
const chLpMultiSelectBtnGroup = document.getElementById("btn-lp-select-group");
const grabberBtnGroup = document.getElementById("grabber-btn-group");

const prTypeBtnGroup = document.getElementById("btn-se-select-group");

const openSearch = document.getElementById("open-search");
const closeResultsWindow = document.getElementById("close-results-window");

const openSearchWindow = document.getElementById("ch-se-tms");
const searchWindow = document.getElementById("search-window");
const closeSearchWindow = document.getElementById("close-search-window");

const openWebWindow = document.getElementById("ch-se-web");
const webWindow = document.getElementById("web-window");
const closeWebWindow = document.getElementById("close-web-window");

const openXmlWindow = document.getElementById("ch-se-xml");
const xmlWindow = document.getElementById("xml-window");
const closeXmlWindow = document.getElementById("close-xml-window");

const closeKeyWindow = document.getElementById("close-key-window");

const openAbout = document.getElementById("open-about");
const aboutWindow = document.getElementById("about-window");
const closeAboutWindow = document.getElementById("close-about-info");

const openSettings = document.getElementById("open-settings");
const settingsWindow = document.getElementById("settings-window");
const closeSettingsWindow = document.getElementById("close-settings");

const openGrabber = document.getElementById("open-grabber");
const grabberWindow = document.getElementById("grabber-window");
const closeGrabberWindow = document.getElementById("close-grabber");

const openMappings = document.getElementById("open-mappings");
const mappingWindow = document.getElementById("mapping-window");
const closeMappingWindow = document.getElementById("close-mappings");

const keyInput = document.getElementById("key-input");
const keyWindow = document.getElementById("key-window");

const chSearch = document.getElementById("search");
const chSearchFilter = document.getElementById("ch_filter");
const searchByChSection = document.getElementsByClassName("search-ch");
const searchByLpSection = document.getElementsByClassName("search-lp");
const searchTable = document.getElementById("search-table");
const channelTable = document.getElementById("channel-table");
const tableSection = document.getElementById("search-results");
const channelSection = document.getElementById("channel-results");
const header = document.getElementById("header");

const regionSelection = document.getElementById("region_selection");
const defaultRegion = document.getElementById("r_none");
const countrySelection = document.getElementById("country_selection");
const allCountries = countrySelection.getElementsByTagName("option");
const defaultCountry = document.getElementById("c_none");
const postalCode = document.getElementById("postal_code");
const providerTypeSelection = document.getElementById("provider_type");
const allLineups = document.getElementById("lineups");
const defaultLineup = document.getElementById("l_none");

const tableClass = document.getElementsByClassName("search-results");

const chInfoWindow = document.getElementById("ch-info-window");
const closeChInfoWindow = document.getElementById("close-ch-info");
const chInfoChName = document.getElementById("chname-input");
const chInfoChCallSign = document.getElementById("tv-callsign");
const chInfoChCallSignLabel = document.getElementById("tv-callsign-label");
const chInfoChId = document.getElementById("tv-id");
const chInfoChIdInput = document.getElementById("tvg-id-input");
const chInfoChIdResult = document.getElementById("tvg-id-result");
const chInfoChIdSave = document.getElementById("tvg-id-save");
const chInfoReplaceInput = document.getElementById("replace-ch");
const chInfoReplaceResult = document.getElementById("replace-ch-result");
const chInfoReplaceNow = document.getElementById("replace-now");
const chInfoImage = document.getElementById("ch-logo");

const daySlider = document.getElementById("days");
const dayNumber = document.getElementById("days_number");
const ratingMapper = document.getElementById("rating_mapper");
const imageType = document.getElementById("image_type");
const imageSize = document.getElementById("image_size");
const ageType = document.getElementById("age_type");
const schedulerRate = document.getElementById("scheduler_rate");
const updateTime = document.getElementById("update_time");
const autoGrab = document.getElementById("auto_grab");
const settingsSave = document.getElementById("settings-save");

const playlistURL = document.getElementById("m3u-url");
const applyPlaylistURL = document.getElementById("m3u-url-apply");
const uploadM3U = document.getElementById("m3u-upload");
const applyUploadM3U = document.getElementById("m3u-upload-apply");

const uploadStation = document.getElementById("station-upload");
const applyUploadStation = document.getElementById("station-upload-apply");

const mappingSection = document.getElementById("missing-mappings");
const mappingTable = document.getElementById("missings-table");

const dlStatusText = document.getElementById("dl_status");
const dlProgress = document.getElementById("grabber_dl");
const dlFileTypeSelection = document.getElementById("file_type");
const dlFileCopyURL = document.getElementById("file_copy");
const dlFileGetFile = document.getElementById("file_dl");
const dlFileCreated = document.getElementById("dl_created");
const startGrabber = document.getElementById("start_dl");
const stopGrabber = document.getElementById("stop_dl");

const xmlName = document.getElementById("xml-name");
const xmlLink = document.getElementById("xml-link");
const addXmlBtn = document.getElementById("xml-select");
const loadXmlBtn = document.getElementById("xml-load");
const removeXmlBtn = document.getElementById("xml-remove");
const xmlSelection = document.getElementById("xml_selection");

const webCountrySelection = document.getElementById("web_country");
const webSelection = document.getElementById("web_selection");

const webUser = document.getElementById("web_user");
const webPw = document.getElementById("web_pw");
const webSendCredentials = document.getElementById("web_send_credentials");

var url_expression = /(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})/gi;
var url_regex = new RegExp(url_expression);

webUser.addEventListener("input", function() {
    if( webUser.value.length > 3 && webPw.value.length > 3 ) {
        webSendCredentials.disabled = false;
    } else {
        webSendCredentials.disabled = true;
    };
});

webPw.addEventListener("input", function() {
    if( webUser.value.length > 3 && webPw.value.length > 3 ) {
        webSendCredentials.disabled = false;
    } else {
        webSendCredentials.disabled = true;
    };
});

webSendCredentials.addEventListener("click", function() {
    saveCredentials();
});

function saveCredentials() {
    var prov_id = webSelection.options[webSelection.selectedIndex].getAttribute("id");

    let s = JSON.stringify({"id": prov_id, "user": webUser.value, "pw": webPw.value})
    fetch("api/save_credentials", {
        method: "POST",
        body: s
    })
    .then(response => {
        response.json().then(function(d) {
            if( d["success"] === true ) {
                console.log(d["message"]);
                loadExtLineupChannels(prov_id);
            } else {
                showNotiMessage(d["message"], "error");
            };
        });
    })
    .catch(error => {
        console.log(error);
        showNotiMessage("An error occurred while serving the request.", "error");
    });
};

xmlName.addEventListener("keyup", function() {
    if( xmlName.value != "" && xmlLink.value.match(url_regex) ) {
        addXmlBtn.disabled = false;
    } else {
        addXmlBtn.disabled = true;
    };
});

xmlLink.addEventListener("keyup", function() {
    if( xmlName.value != "" && xmlLink.value.match(url_regex) ) {
        addXmlBtn.disabled = false;
    } else {
        addXmlBtn.disabled = true;
    };
});

addXmlBtn.addEventListener("click", function() {
    addXmlBtn.textContent = "Adding...";
    addXmlBtn.disabled = true;
    let s = JSON.stringify({"name": xmlName.value, "link": xmlLink.value})
    fetch("api/xmltv_lineups/add", {
        method: "POST",
        body: s
    })
    .then(response => {
        response.json().then(function(d) {
            if( d["success"] === true ) {
                showNotiMessage(d["message"], "success");
                retrieveXmlSources();
            } else {
                showNotiMessage(d["message"], "error");
            };
        });
        addXmlBtn.textContent = "Add provider";
        addXmlBtn.disabled = false;
    })
    .catch(error => {
        console.log(error);
        showNotiMessage("An error occurred while serving the request.", "error");
        addXmlBtn.textContent = "Add provider";
        addXmlBtn.disabled = false;
    });
});

xmlSelection.addEventListener("change", function() {
    var x_type = xmlSelection.options[xmlSelection.options.selectedIndex].getAttribute("id");
    if( x_type != "x_none" ) {
        loadXmlBtn.disabled = false;
        removeXmlBtn.disabled = false;
    } else {
        loadXmlBtn.disabled = true;
        removeXmlBtn.disabled = true;
    };
});

loadXmlBtn.addEventListener("click", function() {
    loadExtLineupChannels(xmlSelection.options[xmlSelection.options.selectedIndex].getAttribute("id"));
});

removeXmlBtn.addEventListener("click", function() {
    var x_type = xmlSelection.options[xmlSelection.options.selectedIndex].getAttribute("id");
    let s = JSON.stringify({"id": x_type})
    fetch("api/xmltv_lineups/remove", {
        method: "POST",
        body: s
    })
    .then(response => {
        response.json().then(function(d) {
            if( d["success"] === true ) {
                showNotiMessage("The EPG source has been removed!", "success");
            } else {
                showNotiMessage(d["message"], "error");
            };
        });
    })
    .catch(error => {
        console.log(error);
        showNotiMessage("An error occurred while serving the request.", "error");
    });
    retrieveXmlSources();
});

function randomInteger(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function retrieveWebSources() {
    var i, L = webSelection.options.length - 1;
    for(i = L; i >= 1; i--) {
        webSelection.remove(i);
    };
    var i, L = webCountrySelection.options.length - 1;
    for(i = L; i >= 1; i--) {
        webCountrySelection.remove(i);
    };
    webSelection.disabled = true;
    openSearchWindow.disabled = true;
    openXmlWindow.disabled = true;
    fetch("app/data/json/providers-"+randomInteger(0,9999999999999)+".json", {
        method: "GET"
    })
    .then(response => {
        response.json().then(function(d) {
            var countryList = [];
            for( i in d ) {
                var t = false;
                if( d[i].hasOwnProperty("menu_visibility") ) {
                    if( d[i]["menu_visibility"] == false ) {
                        t = true;
                    };
                };
                if( t == false ) {
                    var k = "🌐 "
                    if( d[i].hasOwnProperty("auth_req") ) {
                        if ( d[i]["auth_req"] == true ) {
                            k = "🔑 "
                        };
                    };
                    var opt = document.createElement('option');
                    opt.id = i;
                    opt.classList.add(d[i]["country"]);
                    opt.innerHTML = k + d[i]["name"];
                    webSelection.appendChild(opt);
                    
                    if( !countryList.includes(d[i]["country"]) ) {
                        var opt = document.createElement('option');
                        opt.id = d[i]["country"];
                        opt.innerHTML = d[i]["country"];
                        webCountrySelection.appendChild(opt);
                        countryList.push(d[i]["country"]);
                    };
                };
            };
        });
        openSearchWindow.disabled = false;
        openXmlWindow.disabled = false;
    })
    .catch(error => {
        console.log(error);
        showNotiMessage("An error occurred while serving the request.", "error");
        openSearchWindow.disabled = false;
        openXmlWindow.disabled = false;
    });
};

webCountrySelection.addEventListener("change" , function() {
    webUser.disabled = true;
    webPw.disabled = true;
    webUser.value = "";
    webPw.value = "";
    webSendCredentials.disabled = true;
    var wcso = webCountrySelection.options;
    var wso = webSelection.options;
    wso[0].selected = 'selected';
    var selectedWebRegion = wcso[webCountrySelection.selectedIndex].getAttribute("id");
    if( selectedWebRegion != "wc_none" ) {
        for( var i = 0; i < webSelection.options.length; i++ ) {
            if( wso[i].classList.contains(selectedWebRegion) ) {
                wso[i].hidden = false;
            } else {
                wso[i].hidden = true;
            };
        };
        webSelection.disabled = false;
    } else {
        webSelection.disabled = true;
    };
});

webSelection.addEventListener("change", function() {
    webUser.disabled = true;
    webPw.disabled = true;
    webUser.value = "";
    webPw.value = "";
    webSendCredentials.disabled = true;
    var wp_id = webSelection.options[webSelection.selectedIndex].getAttribute("id");
    if( wp_id != "wp_none" ) {
        loadExtLineupChannels(wp_id);
    };    
});

function retrieveXmlSources() {
    openSearchWindow.disabled = true;
    openWebWindow.disabled = true;
    var i, L = xmlSelection.options.length - 1;
    for(i = L; i >= 1; i--) {
        xmlSelection.remove(i);
    };
    xmlName.value = "";
    xmlLink.value = "";
    addXmlBtn.disabled = true;
    loadXmlBtn.disabled = true;
    removeXmlBtn.disabled = true;
    fetch("api/xmltv_lineups/get", {
        method: "GET"
    })
    .then(response => {
        response.json().then(function(d) {
            if( d["success"] === true ) {
                for( i in d["result"] ) {
                    var opt = document.createElement('option');
                    opt.id = i;
                    opt.innerHTML = d["result"][i]["name"];
                    xmlSelection.appendChild(opt);
                };
            } else {
                showNotiMessage(d["message"], "error");
            };
        });
        openSearchWindow.disabled = false;
        openWebWindow.disabled = false;
    })
    .catch(error => {
        console.log(error);
        showNotiMessage("An error occurred while serving the request.", "error");
        openSearchWindow.disabled = false;
        openWebWindow.disabled = false;
    });
};

dlFileCopyURL.addEventListener("click", function() {
    var f_type = dlFileTypeSelection.options[dlFileTypeSelection.options.selectedIndex].getAttribute("id");
    var temp = document.createElement("input");
    temp.style.opacity = 0;
    document.body.append(temp);
    if( f_type === "XML" ) {
        temp.value = document.location.href + "download/epg.xml";
    } else if( f_type === "GZ" ) {
        temp.value = document.location.href + "download/epg.xml.gz";
    };
    temp.focus();
    temp.select();
    document.execCommand("copy");
    temp.remove();
    dlFileCopyURL.disabled = true;
    dlFileCopyURL.textContent = "Link copied!"
    setTimeout(function() {dlFileCopyURL.disabled = false; dlFileCopyURL.textContent = "Copy link";}, 1000);
});

dlFileGetFile.addEventListener("click", function() {
    var f_type;
    if( dlFileTypeSelection.options[dlFileTypeSelection.selectedIndex].getAttribute("id") === "XML" ) {
        f_type = document.location.href + "download/epg.xml";
    } else if( dlFileTypeSelection.options[dlFileTypeSelection.selectedIndex].getAttribute("id") === "GZ" ) {
        f_type = document.location.href + "download/epg.xml.gz";
    };
    window.location.href = f_type;
});

chMap.addEventListener("click", function() {
    var chSelected = document.getElementsByClassName("ch_selected")[0].getAttribute("id").replace("ch_", "");
    var mpSelected = document.getElementsByClassName("mp_selected")[0];
    addTvgId(chSelected, mpSelected.value);
    loadSettings(mappingTable.getElementsByTagName("tbody")[0].scrollTop);
    chMap.disabled = true;
    mainBtnGroup.style.display = "inline";
    chMultiSelectBtnGroup.style.display = "none";
});

function insertMissingMappings(overview, position) {
    mappingTable.innerHTML = "";
    for( i in overview ) {
        if( overview[i]["mapped"] != true ) {
            var newRow = mappingTable.insertRow()
            newRow.innerHTML = "<td>" + overview[i]["name"] + "<p>" + i + "</p></td>";
            newRow.value = i;
            newRow.classList.add("mp_row");
            newRow.addEventListener("click", function() {
                if( this.classList.contains("mp_selected") ) {
                    this.classList.remove("mp_selected");
                    chMap.disabled = true;
                } else {
                    mpChListings = mappingTable.getElementsByTagName("tr");
                    for( let i = 0; i < mpChListings.length; i++ ) {
                        mpChListings[i].classList.remove("mp_selected");
                    };
                    this.classList.add("mp_selected");
                    var chRows = document.getElementsByClassName("ch_selected");
                    if( chRows.length === 1 ) {
                        chMap.disabled = false;
                    } else {
                        chMap.disabled = true;
                    };
                };
            });
        };
    };
    if( document.getElementsByClassName("mp_row").length > 0 ) {
        mappingSection.style.display = "block";
        section = document.getElementsByClassName("search-results");
        for( let i = 0; i < section.length; i++ ) {
            section[i].getElementsByTagName("table")[0].classList.add("reduce-height");
        };
        mappingTable.getElementsByTagName("tbody")[0].scroll(0, position);  
    } else {
        mappingSection.style.display = "none";
    };
};

playlistURL.addEventListener("keyup", function() {
    if( playlistURL.value != "" && (playlistURL.value.includes("http://") || playlistURL.value.includes("https://")) ) {
        applyPlaylistURL.disabled = false;
    } else {
        applyPlaylistURL.disabled = true;
    };
});

applyPlaylistURL.addEventListener("click", function() {
    fetch("api/playlist-link", {
        method: "POST",
        body: JSON.stringify({"link": playlistURL.value})
    })
    .then(response => {
        response.json().then(function(e) {
            if( e["success"] === true ) {
                showNotiMessage("The playlist link has been saved!", "success");
                insertMissingMappings(e["result"], 0);
                mappingWindow.classList.add("nav-bar-move");
                blockPage.style.display = "none";
                mainBtnGroup.style.display = "inline";
                setTimeout(function() {mappingWindow.style.display = "none"; mappingWindow.classList.remove("add-blocker"); mappingWindow.classList.remove("nav-bar-move")}, 600);
            };
        });
    })
    .catch(error => {
        console.log(error);
        showNotiMessage("An error occurred while serving the request.", "error");
    });
});

uploadM3U.addEventListener("change", function(e) {
    if( uploadM3U.value != "" ) {
        applyUploadM3U.disabled = false;
    } else {
        applyUploadM3U.disabled = true;
    };
});

applyUploadM3U.addEventListener("click", function() {
    fetch("api/playlist-m3u", {
        method: "POST",
        body: uploadM3U.files[0]
    })
    .then(response => {
        response.json().then(function(e) {
            if( e["success"] === true ) {
                showNotiMessage("The playlist file has been saved!", "success");
                insertMissingMappings(e["result"], 0);
                mappingWindow.classList.add("nav-bar-move");
                blockPage.style.display = "none";
                mainBtnGroup.style.display = "inline";
                setTimeout(function() {mappingWindow.style.display = "none"; mappingWindow.classList.remove("add-blocker"); mappingWindow.classList.remove("nav-bar-move")}, 600);
            } else {
                showNotiMessage("Upload failed. Please use UTF-8 encoded files only.", "error");
            };
        });
    })
    .catch(error => {
        console.log(error);
        showNotiMessage("An error occurred while serving the request.", "error");
    })
});

uploadStation.addEventListener("change", function(e) {
    if( uploadStation.value != "" ) {
        applyUploadStation.disabled = false;
    } else {
        applyUploadStation.disabled = true;
    };
});

applyUploadStation.addEventListener("click", function() {
    fetch("api/add", {
        method: "POST",
        body: uploadStation.files[0]
    })
    .then(response => {
        response.json().then(function(e) {
            if( e["success"] === true ) {
                showNotiMessage("The channel has been added!", "success");
                loadChannelList();
            } else {
                showNotiMessage("Upload failed. Please use station config files only.", "error");
            };
        });
    })
    .catch(error => {
        console.log(error);
        showNotiMessage("An error occurred while serving the request.", "error");
    })
});

let typingTimer;
let doneTypingInterval = 600;

chSearchBar.addEventListener("keypress", function(button) {
    clearTimeout(typingTimer);
    if( button.key === 'Enter' && chSearchBar.value != "" ) {
        doneTypingChannel(true);
    } else if (chSearchBar.value) {
        typingTimer = setTimeout(doneTypingChannel(false), 400);
    };
});

function doneTypingChannel(status) {
    var searchText = chSearchBar.value;
    var channelRows = channelTable.getElementsByTagName("tr");
    var currentPosition = channelTable.getElementsByTagName("tbody")[0].scrollTop;
    var chGotResult = false;
    var firstEncounter = null;
    for( var i = 0; i < channelRows.length; i++ ) {
        if( channelRows[i].getElementsByTagName("td")[1].innerHTML.split("<p>")[0].toLowerCase().includes(searchText.toLowerCase()) ) {
            chGotResult = true;
            if( firstEncounter === null ) {
                firstEncounter = i;
            };
            if( status === true && Math.ceil(currentPosition) >= channelRows[i].offsetTop ) {
                continue;
            };
            channelTable.getElementsByTagName("tbody")[0].scroll(0, channelRows[i].offsetTop);
            break;
        };
        if( i === (channelRows.length - 1) && chGotResult === true ) {
            channelTable.getElementsByTagName("tbody")[0].scroll(0, channelRows[firstEncounter].offsetTop);
        };
    };
    if( chGotResult === false ) {
        showNotiMessage("Channel not found.");
    };
};

lpSearchBar.addEventListener("keypress", function(button) {
    clearTimeout(typingTimer);
    if( button.key === 'Enter' && lpSearchBar.value != "" ) {
        doneTypingLpChannel(true);
    } else if (lpSearchBar.value) {
        typingTimer = setTimeout(doneTypingLpChannel(false), 400);
    };
});

function doneTypingLpChannel(status) {
    var searchText = lpSearchBar.value;
    var channelRows = searchTable.getElementsByTagName("tr");
    var currentPosition = searchTable.getElementsByTagName("tbody")[0].scrollTop;
    var chGotResult = false;
    var firstEncounter = null;
    for( var i = 0; i < channelRows.length; i++ ) {
        if( channelRows[i].getElementsByTagName("td")[1].innerHTML.split("<p>")[0].toLowerCase().includes(searchText.toLowerCase()) ) {
            chGotResult = true;
            if( firstEncounter === null ) {
                firstEncounter = i;
            };
            if( status === true && Math.ceil(currentPosition) >= channelRows[i].offsetTop ) {
                continue;
            };
            searchTable.getElementsByTagName("tbody")[0].scroll(0, channelRows[i].offsetTop);
            break;
        };
        if( i === (channelRows.length - 1) && chGotResult === true ) {
            searchTable.getElementsByTagName("tbody")[0].scroll(0, channelRows[firstEncounter].offsetTop);
        };
    };
    if( chGotResult === false ) {
        showNotiMessage("Channel not found.");
    };
};

// apiCheck(null);
grabberCheckAutoUpdate();
loadChannelList();
loadSettings(0);
mainBtnGroup.style.display = "inline";
blockPage.style.display = "none";
showNotiMessage("Welcome to easyepg!");

function apiCheck(key) {
    openXmlWindow.disabled = true;
    openWebWindow.disabled = true;
    fetch("api/key_check", {
        method: "POST",
        body: JSON.stringify({"key": key})
    })
    .then(response => {
        response.json().then(function(i) {
            if( i["success"] === true ) {
                keyWindow.classList.add("nav-bar-move");
                setTimeout(function() {keyWindow.style.display = "none"; keyWindow.classList.remove("add-blocker"); keyWindow.classList.remove("nav-bar-move");}, 600);
                loadTmsEvent();
                blockPage.removeEventListener("click", closeKeyWindowEvent);
                blockPage.addEventListener("click", closeSearchWindowEvent);
                searchWindow.style.display = "inline";
            } else {
                if( keyInput.value.length > 0 ) {
                    showNotiMessage("Your key is invalid.", "error");
                };
                blockPage.addEventListener("click", closeKeyWindowEvent);
                enterApiKey();
            };
            openXmlWindow.disabled = false;
            openWebWindow.disabled = false;
        });
    })
    .catch(error => {
        openXmlWindow.disabled = false;
        openWebWindow.disabled = false;
        console.log(error);
        showNotiMessage("An error occurred while serving the request.", "error");
    });
};

startGrabber.addEventListener("click", function() {
    blockPage.removeEventListener("click", closeGrabberWindowEvent);
    startGrabber.disabled = true;
    stopGrabber.disabled = false;
    dlStatusText.innerText = "Starting...";
    closeGrabberWindow.style.display = "none";
    dlProgress.value = 0;
    fetch("api/start-grabber", {
        method: "GET"
    })
    .then(response => {
        response.json().then(function(i) {
            if( i["success"] === true ) {
                grabberCheckAutoUpdate();
            };
        });
    })
    .catch(error => {
        console.log(error);
        dlStatusText.innerText = "An error occurred. Please reload the page.";
        showNotiMessage("An error occurred while serving the request.", "error");
    });
});

stopGrabber.addEventListener("click", function() {
    stopGrabber.disabled = true;
    fetch("api/stop-grabber", {
        method: "GET"
    })
    .then(response => {
        response.json().then(function(i) {
            if( i["success"] === true ) {
                // ...
            };
        });
    })
    .catch(error => {
        console.log(error);
        showNotiMessage("An error occurred while serving the request.", "error");
    });
});

function grabberCheckAutoUpdate() {
    var interval = window.setInterval(function() {
        fetch("api/grabber-status", {
            method: "GET"
        })
        .then(response => {
            response.json().then(function(i) {
                if( i["success"] === true ) {
                    var r = i["result"];
                    if( r["status"].includes("Downloading") ) {
                        dlStatusText.innerText = r["status"]+ " ("+r["progress"]*2+"%)";
                    } else {
                        dlStatusText.innerText = r["status"]
                    };
                    dlProgress.value = r["progress"];
                    if( r["file_available"] === true ) {
                        dlFileCopyURL.disabled = false;
                        dlFileGetFile.disabled = false;
                        dlFileCreated.innerText = r["file_created"];
                    };
                    if( r["grabbing"] === true ) {
                        startGrabber.style.display = "none";
                        startGrabber.disabled = false;
                        stopGrabber.style.display = "inline";
                        grabberWindow.style.display = "inline";
                        closeGrabberWindow.style.display = "none";
                        blockPage.classList.add("add-blocker");
                        blockPage.style.display = "inline";
                        blockPage.removeEventListener("click", closeGrabberWindowEvent);
                        mainBtnGroup.style.display = "none";
                        grabberBtnGroup.style.display = "inline";
                    } else {
                        clearInterval(interval);
                        blockPage.addEventListener("click", closeGrabberWindowEvent);
                        closeGrabberWindow.style.display = "inline";
                        startGrabber.style.display = "inline";
                        startGrabber.disabled = false;
                        stopGrabber.style.display = "none";
                    };
                };
            });
        })
        .catch(error => {
            dlStatusText.innerText = "Failed to fetch the status. Please reload the page.";
            dlProgress.value = 0;
            startGrabber.style.display = "none";
            stopGrabber.style.display = "none";
            clearInterval(interval);
            console.log(error);
            showNotiMessage("An error occurred while serving the request.", "error");
        });
    }, 1000);
};

function loadSettings (mapTablePosition) {
    fetch("api/settings", {
        method: "GET"
    })
    .then(response => {
        response.json().then(function(i) {
            if( i["file"] === true ) {
                if( i.hasOwnProperty("file_url") ) {
                    fetch("api/playlist-link", {
                        method: "GET"
                    })
                    .then(response => {
                        response.json().then(function(e) {
                            if( e["success"] === true ) {
                                insertMissingMappings(e["result"], mapTablePosition);
                            };
                        });
                    })
                    .catch(error => {
                        console.log(error);
                        showNotiMessage("An error occurred while serving the request.", "error");
                    });
                } else {
                    fetch("api/playlist-m3u", {
                        method: "GET"
                    })
                    .then(response => {
                        response.json().then(function(e) {
                            if( e["success"] === true ) {
                                insertMissingMappings(e["result"], mapTablePosition);
                            };
                        });
                    })
                    .catch(error => {
                        console.log(error);
                        showNotiMessage("An error occurred while serving the request.", "error");
                    });
                };
            };
            daySlider.value = i["days"];
            dayNumber.textContent = i["days"];
            document.getElementById("rm_" + i["rm"]).selected = true;
            document.getElementById("it_" + i["it"]).selected = true;
            document.getElementById("is_" + i["is"]).selected = true;
            document.getElementById("at_" + i["at"]).selected = true;
            document.getElementById("rate_" + i["rate"]).selected = true;
            updateTime.value = i["ut"];
            document.getElementById("ag_" + i["ag"]).selected = true;
        });
    })
    .catch(error => {
        console.log(error);
        showNotiMessage("An error occurred while serving the request.", "error");
    });
};

settingsSave.addEventListener("click", function() {
    saveSettings();
});

function saveSettings () {
    if( updateTime.value == "" || updateTime.value == "--:--" ) {
        updateTime.value = "04:00";
    };
    fetch("api/save_settings", {
        method: "POST",
        body: JSON.stringify({"days": daySlider.value, "rm": ratingMapper.options[ratingMapper.selectedIndex].getAttribute("id").replace("rm_", ""), "it": imageType.options[imageType.selectedIndex].getAttribute("id").replace("it_", ""), "is": imageSize.options[imageSize.selectedIndex].getAttribute("id").replace("is_", ""), "at": ageType.options[ageType.selectedIndex].getAttribute("id").replace("at_", ""), "rate": schedulerRate.options[schedulerRate.selectedIndex].getAttribute("id").replace("rate_", ""), "ut": updateTime.value, "ag": autoGrab.options[autoGrab.selectedIndex].getAttribute("id").replace("ag_", "")})
    })
    .then(response => {
        response.json().then(function(i) {
            if( i["success"] === true ) {
                showNotiMessage("Settings saved!", "success");
            } else {
                showNotiMessage(i["message"], "error");
            };
        });
    })
    .catch(error => {
        console.log(error);
        showNotiMessage("An error occurred while serving the request.", "error");
    });
};

function enterApiKey() {
    keyWindow.style.display = "inline";
    blockPage.classList.add("add-blocker");
    blockPage.style.display = "inline";
};

keyInput.addEventListener("keyup", function() {
    if( keyInput.value.length === 24 ) {
        apiCheck(keyInput.value);
    };
});

daySlider.addEventListener("input", function() {
    dayNumber.textContent = daySlider.value;
});

chInfoChIdInput.addEventListener("keyup", function() {
    chInfoChIdResult.value = "";
    chInfoChIdSave.disabled = true;
    clearTimeout(typingTimer);
    if (chInfoChIdInput.value != "") {
        typingTimer = setTimeout(doneTypingEpgId, doneTypingInterval);
    } else if (chInfoChIdInput.value === "") {
        chInfoChIdSave.disabled = false;
        chInfoChIdResult.value = "REMOVE TVG ID";
    };
});

function doneTypingEpgId() {
    fetch("api/check-tvgid", {
        method: "POST",
        body: JSON.stringify({"tvg-id": chInfoChIdInput.value})
    })
    .then(response => {
        response.json().then(function(i) {
            if( i["success"] === true ) {
                chInfoChIdResult.value = "CHECK OK";
                chInfoChIdSave.disabled = false;
            } else {
                chInfoChIdResult.value = i["message"];
            };
        });
    })
    .catch(error => {
        console.log(error);
        showNotiMessage("An error occurred while serving the request.", "error");
    });
};

chSelectAll.addEventListener("click", function() {
    var channelRows = document.getElementsByClassName("ch_row");
    for( let i = 0; i < channelRows.length; i++ ) {
        channelRows[i].classList.add("ch_selected");
    };
});

chLpSelectAll.addEventListener("click", function() {
    var channelRows = document.getElementsByClassName("mn_row");
    for( let i = 0; i < channelRows.length; i++ ) {
        if( !channelRows[i].classList.contains("mn_added") ) {
            channelRows[i].classList.add("ch_selected");
        };
    };
});

chUnselectAll.addEventListener("click", function() {
    var channelRows = document.getElementsByClassName("ch_row");
    var channelInfoElements = document.getElementsByClassName("info-ch");
    for( let i = 0; i < channelRows.length; i++ ) {
        if( channelRows[i].classList.contains("ch_selected") ) {
            channelRows[i].classList.remove("ch_selected");
        };
        channelInfoElements[i].classList.remove("info-ch-disabled");
        channelInfoElements[i].disabled = false;
    };
    chMultiSelectBtnGroup.style.display = "none";
    mainBtnGroup.style.display = "inline";
});

chLpUnselectAll.addEventListener("click", function() {
    var channelRows = document.getElementsByClassName("mn_row");
    var channelInfoElements = document.getElementsByClassName("add-ch");
    for( let i = 0; i < channelRows.length; i++ ) {
        if( channelRows[i].classList.contains("ch_selected") ) {
            channelRows[i].classList.remove("ch_selected");
        };
        if( !channelRows[i].classList.contains("mn_added") ) {
            channelInfoElements[i].classList.remove("add-ch-disabled");
        };
        channelInfoElements[i].disabled = false;
    };
    chLpMultiSelectBtnGroup.style.display = "none";
    mainBtnGroup.style.display = "inline";
});

chRemoveAll.addEventListener("click", function() {
    var channelRows = document.getElementsByClassName("ch_row");
    var toBeRemovedList = [];
    for( let i = 0; i < channelRows.length; i++ ) {
        if( channelRows[i].classList.contains("ch_selected") ) {
            toBeRemovedList.push(channelRows[i].getAttribute("id").replace("ch_", ""));
        };
    };
    fetch("api/remove", {
        method: "POST",
        body: JSON.stringify({"ids": toBeRemovedList})
    })
    .then(response => {
        response.json().then(function(i) {
            if( i["success"] === true ) {
                showNotiMessage(toBeRemovedList.length + " channel(s) removed successfully!", "success");
                loadChannelList();
                loadSettings(0);
                chMultiSelectBtnGroup.style.display = "none";
                mainBtnGroup.style.display = "inline";
            } else {
                showNotiMessage(i["message"], "error");
            };
        });
    })
    .catch(error => {
        console.log(error);
        showNotiMessage("An error occurred while serving the request.", "error");
    });
});

chLpAddAll.addEventListener("click", function() {
    var channelRows = document.getElementsByClassName("mn_row");
    var toBeAddedList = [];
    for( let i = 0; i < channelRows.length; i++ ) {
        if( channelRows[i].classList.contains("ch_selected") ) {
            toBeAddedList.push(channelRows[i].getAttribute("id").replace("mn|", ""));
        };
    };
    fetch("api/add", {
        method: "POST",
        body: JSON.stringify({"ids": toBeAddedList})
    })
    .then(response => {
        response.json().then(function(i) {
            if( i["success"] === true ) {
                showNotiMessage(toBeAddedList.length + " channel(s) added successfully!", "success");
                for ( let i = 0; i < toBeAddedList.length; i++ ) {
                    if( toBeAddedList[i].includes("|") ) {
                        var v = toBeAddedList[i].split("|")[1];
                    } else {
                        var v = toBeAddedList[i];
                    };
                    var elemTr = document.getElementById("mn|" + toBeAddedList[i]);
                    var elem = document.getElementById(v);
                    elem.classList.remove("add-ch-disabled");
                    elem.classList.add("added-ch");
                    elem.disabled = true;
                    elem.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="currentColor" class="bi bi-check2-circle" viewBox="0 0 16 16"><path d="M2.5 8a5.5 5.5 0 0 1 8.25-4.764.5.5 0 0 0 .5-.866A6.5 6.5 0 1 0 14.5 8a.5.5 0 0 0-1 0 5.5 5.5 0 1 1-11 0z"/><path d="M15.354 3.354a.5.5 0 0 0-.708-.708L8 9.293 5.354 6.646a.5.5 0 1 0-.708.708l3 3a.5.5 0 0 0 .708 0l7-7z"/></svg>';
                    elemTr.classList.remove("ch_selected");
                    elemTr.classList.add("mn_added");
                };
                var channelRows = document.getElementsByClassName("mn_row");
                for( let i = 0; i < channelRows.length; i++ ) {
                    if( !channelRows[i].classList.contains("mn_added") ) {
                        channelRows[i].getElementsByTagName("button")[0].classList.remove("add-ch-disabled");
                        channelRows[i].getElementsByTagName("button")[0].disabled = false;
                    };
                };
                chLpMultiSelectBtnGroup.style.display = "none";
                mainBtnGroup.style.display = "inline";
            } else {
                showNotiMessage(i["message"], "error");
            };
        });
    })
    .catch(error => {
        console.log(error);
        showNotiMessage("An error occurred while serving the request.", "error");
    });
});

openAbout.addEventListener("click", function() {
    aboutWindow.style.display = "inline";
    blockPage.classList.add("add-blocker");
    blockPage.style.display = "inline";
    mainBtnGroup.style.display = "none";
    aboutBtnGroup.style.display = "inline";
    blockPage.addEventListener("click", closeAboutWindowEvent);
});

closeAboutWindow.addEventListener("click", closeAboutWindowEvent);

function closeAboutWindowEvent() {
    aboutWindow.classList.add("nav-bar-move");
    blockPage.style.display = "none";
    blockPage.removeEventListener("click", closeAboutWindowEvent);
    mainBtnGroup.style.display = "inline";
    aboutBtnGroup.style.display = "none";
    setTimeout(function() {aboutWindow.style.display = "none"; aboutWindow.classList.remove("add-blocker"); aboutWindow.classList.remove("nav-bar-move")}, 600);
};

openMappings.addEventListener("click", function() {
    mappingWindow.style.display = "inline";
    blockPage.classList.add("add-blocker");
    blockPage.style.display = "inline";
    mainBtnGroup.style.display = "none";
    blockPage.addEventListener("click", closeMappingWindowEvent);
});

closeMappingWindow.addEventListener("click", closeMappingWindowEvent);

function closeMappingWindowEvent() {
    mappingWindow.classList.add("nav-bar-move");
    blockPage.style.display = "none";
    blockPage.removeEventListener("click", closeMappingWindowEvent);
    mainBtnGroup.style.display = "inline";
    setTimeout(function() {mappingWindow.style.display = "none"; mappingWindow.classList.remove("add-blocker"); mappingWindow.classList.remove("nav-bar-move")}, 600);
};

openSettings.addEventListener("click", function() {
    settingsWindow.style.display = "inline";
    blockPage.classList.add("add-blocker");
    blockPage.style.display = "inline";
    mainBtnGroup.style.display = "none";
    blockPage.addEventListener("click", closeSettingsWindowEvent);
});

closeSettingsWindow.addEventListener("click", closeSettingsWindowEvent);

function closeSettingsWindowEvent() {
    settingsWindow.classList.add("nav-bar-move");
    blockPage.style.display = "none";
    blockPage.removeEventListener("click", closeSettingsWindowEvent);
    mainBtnGroup.style.display = "inline";
    setTimeout(function() {settingsWindow.style.display = "none"; settingsWindow.classList.remove("add-blocker"); settingsWindow.classList.remove("nav-bar-move")}, 600);
};

openGrabber.addEventListener("click", function() {
    startGrabber.style.display = "none";
    stopGrabber.style.display = "none";
    grabberCheckAutoUpdate();
    grabberWindow.style.display = "inline";
    blockPage.classList.add("add-blocker");
    blockPage.style.display = "inline";
    mainBtnGroup.style.display = "none";
    grabberBtnGroup.style.display = "inline";
    blockPage.addEventListener("click", closeGrabberWindowEvent);
});

closeGrabberWindow.addEventListener("click", closeGrabberWindowEvent);

function closeGrabberWindowEvent() {
    grabberWindow.classList.add("nav-bar-move");
    blockPage.style.display = "none";
    blockPage.removeEventListener("click", closeGrabberWindowEvent);
    grabberBtnGroup.style.display = "none";
    mainBtnGroup.style.display = "inline";
    setTimeout(function() {grabberWindow.style.display = "none"; grabberWindow.classList.remove("add-blocker"); grabberWindow.classList.remove("nav-bar-move")}, 600);
};

function showNotiMessage(content, notiType) {
    var newNoti = document.createElement('nav');
    var newNotiId = document.getElementsByClassName("nav-top").length + 1;
    newNoti.id = "noti-bar-" + newNotiId;
    newNoti.classList.add("nav-top");
    newNoti.classList.add("noti");
    newNoti.style.display = "none";
    newNoti.innerHTML = "<span>" + content + "</span>";
    if( notiType === "success" ) {
        newNoti.classList.add("noti-success");
    } else if ( notiType === "error" ) {
        newNoti.classList.add("noti-error");
    } else {
        newNoti.classList.add("noti-info");
    };
    document.body.appendChild(newNoti);
    newNoti.classList.add("noti-show");
    newNoti.style.display = "inline";
    setTimeout(function() {
        newNoti.remove();
    }, 2900);
};

openSearchWindow.addEventListener("click", function() {
    if( !openSearchWindow.classList.contains("selected-btn") ) {
        if( openWebWindow.classList.contains("selected-btn") ) {
            webWindow.classList.add("nav-bar-move");
            blockPage.removeEventListener("click", closeWebWindowEvent);
            setTimeout(function() {webWindow.style.display = "none"; webWindow.classList.remove("nav-bar-move")}, 600);
            openWebWindow.classList.remove("selected-btn");
        };
        if( openXmlWindow.classList.contains("selected-btn") ) {
            xmlWindow.classList.add("nav-bar-move");
            blockPage.removeEventListener("click", closeXmlWindowEvent);
            setTimeout(function() {xmlWindow.style.display = "none"; xmlWindow.classList.remove("nav-bar-move")}, 600);
            openXmlWindow.classList.remove("selected-btn");
        };
        openSearchWindow.classList.add("selected-btn");
        apiCheck(null);
    };
});

closeSearchWindow.addEventListener("click", closeSearchWindowEvent);

function closeSearchWindowEvent() {
    searchWindow.classList.add("nav-bar-move");
    blockPage.style.display = "none";
    blockPage.removeEventListener("click", closeSearchWindowEvent);
    prTypeBtnGroup.style.display = "none";
    mainBtnGroup.style.display = "inline";
    setTimeout(function() {searchWindow.style.display = "none"; blockPage.classList.remove("add-blocker"); searchWindow.classList.remove("nav-bar-move")}, 600);
};

closeKeyWindow.addEventListener("click", closeKeyWindowEvent);

function closeKeyWindowEvent() {
    keyWindow.classList.add("nav-bar-move");
    blockPage.style.display = "none";
    blockPage.removeEventListener("click", closeKeyWindowEvent);
    prTypeBtnGroup.style.display = "none";
    mainBtnGroup.style.display = "inline";
    setTimeout(function() {keyWindow.style.display = "none"; blockPage.classList.remove("add-blocker"); keyWindow.classList.remove("nav-bar-move")}, 600);
};

openWebWindow.addEventListener("click", function() {
    if( !openWebWindow.classList.contains("selected-btn") ) {
        if( openSearchWindow.classList.contains("selected-btn") ) {
            if( keyWindow.style.display === "inline" ) {
                keyWindow.classList.add("nav-bar-move");
                blockPage.removeEventListener("click", closeKeyWindowEvent);
                setTimeout(function() {keyWindow.style.display = "none"; keyWindow.classList.remove("nav-bar-move")}, 600);
            } else {
                searchWindow.classList.add("nav-bar-move");
                blockPage.removeEventListener("click", closeSearchWindowEvent);
                setTimeout(function() {searchWindow.style.display = "none"; searchWindow.classList.remove("nav-bar-move")}, 600);
            };
            openSearchWindow.classList.remove("selected-btn");
        };
        if( openXmlWindow.classList.contains("selected-btn") ) {
            xmlWindow.classList.add("nav-bar-move");
            blockPage.removeEventListener("click", closeXmlWindowEvent);
            setTimeout(function() {xmlWindow.style.display = "none"; xmlWindow.classList.remove("nav-bar-move")}, 600);
            openXmlWindow.classList.remove("selected-btn");
        };
        blockPage.addEventListener("click", closeWebWindowEvent);
        openWebWindow.classList.add("selected-btn");
        retrieveWebSources();
        webWindow.style.display = "inline";
    };
});

closeWebWindow.addEventListener("click", closeWebWindowEvent);

function closeWebWindowEvent() {
    webWindow.classList.add("nav-bar-move");
    blockPage.style.display = "none";
    blockPage.removeEventListener("click", closeWebWindowEvent);
    prTypeBtnGroup.style.display = "none";
    mainBtnGroup.style.display = "inline";
    setTimeout(function() {webWindow.style.display = "none"; blockPage.classList.remove("add-blocker"); webWindow.classList.remove("nav-bar-move")}, 600);
};

openXmlWindow.addEventListener("click", function() {
    if( !openXmlWindow.classList.contains("selected-btn") ) {
        if( openSearchWindow.classList.contains("selected-btn") ) {
            if( keyWindow.style.display === "inline" ) {
                keyWindow.classList.add("nav-bar-move");
                blockPage.removeEventListener("click", closeKeyWindowEvent);
                setTimeout(function() {keyWindow.style.display = "none"; keyWindow.classList.remove("nav-bar-move")}, 600);
            } else {
                searchWindow.classList.add("nav-bar-move");
                blockPage.removeEventListener("click", closeSearchWindowEvent);
                setTimeout(function() {searchWindow.style.display = "none"; searchWindow.classList.remove("nav-bar-move")}, 600);
            };
            openSearchWindow.classList.remove("selected-btn");
        };
        if( openWebWindow.classList.contains("selected-btn") ) {
            webWindow.classList.add("nav-bar-move");
            blockPage.removeEventListener("click", closeWebWindowEvent);
            setTimeout(function() {webWindow.style.display = "none"; webWindow.classList.remove("nav-bar-move")}, 600);
            openWebWindow.classList.remove("selected-btn");
        };
        blockPage.addEventListener("click", closeXmlWindowEvent);
        openXmlWindow.classList.add("selected-btn");
        retrieveXmlSources();
        xmlWindow.style.display = "inline";
    };
});

closeXmlWindow.addEventListener("click", closeXmlWindowEvent);

function closeXmlWindowEvent() {
    xmlWindow.classList.add("nav-bar-move");
    blockPage.style.display = "none";
    blockPage.removeEventListener("click", closeXmlWindowEvent);
    prTypeBtnGroup.style.display = "none";
    mainBtnGroup.style.display = "inline";
    setTimeout(function() {xmlWindow.style.display = "none"; blockPage.classList.remove("add-blocker"); xmlWindow.classList.remove("nav-bar-move")}, 600);
};

openSearch.addEventListener("click", function() {
    if( openWebWindow.classList.contains("selected-btn") ) {
        retrieveWebSources();
        webWindow.style.display = "inline";
        blockPage.addEventListener("click", closeWebWindowEvent);
    } else if( openSearchWindow.classList.contains("selected-btn") ) {
        apiCheck(null);
    } else if( openXmlWindow.classList.contains("selected-btn") ) {
        retrieveXmlSources();
        xmlWindow.style.display = "inline";
        blockPage.addEventListener("click", closeXmlWindowEvent);
    };
    blockPage.classList.add("add-blocker");
    blockPage.style.display = "inline";
    mainBtnGroup.style.display = "none";
    prTypeBtnGroup.style.display = "inline";
    webUser.disabled = true;
    webPw.disabled = true;
    webUser.value = "";
    webPw.value = "";
    webSendCredentials.disabled = true;
});

function loadTmsEvent() {
    chSearch.value = "";
    if( getCookie("LineupFilter") != "" ) {
        var filterData = JSON.parse(getCookie("LineupFilter"));
        document.getElementById(filterData["Region"]).selected = true;
        document.getElementById(filterData["Country"]).selected = true;
        countrySelection.disabled = false;
        postalCode.value = filterData["PostalCode"];
        postalCode.disabled = false;
        document.getElementById(filterData["ServiceType"]).selected = true;
        doneTypingPostalCode();
    } else {
        defaultLineup.selected = "true";
    };
};

closeChInfoWindow.addEventListener("click", closeChInfoWindowEvent);

function closeChInfoWindowEvent() {
    chInfoWindow.classList.add("nav-bar-move");
    blockPage.style.display = "none";
    blockPage.removeEventListener("click", closeChInfoWindowEvent);
    mainBtnGroup.style.display = "inline";
    setTimeout(function() {chInfoWindow.style.display = "none"; blockPage.classList.remove("add-blocker"); chInfoWindow.classList.remove("nav-bar-move")}, 600);
};

chInfoReplaceInput.addEventListener("keyup", function() {
    chInfoReplaceNow.disabled = true;
    chInfoReplaceResult.value = "";
    clearTimeout(typingTimer);
    if( chInfoReplaceInput.value ) {
        typingTimer = setTimeout(doneTypingId, doneTypingInterval);
    };
});

function doneTypingId() {
    fetch("api/channel_info", {
        method: "POST",
        body: JSON.stringify({"id": chInfoReplaceInput.value})
    })
    .then(response => {
        response.json().then(function(i) {
            if( i["success"] === true ) {
                chInfoReplaceResult.value = i["result"][0]["name"];
                chInfoReplaceNow.disabled = false;
                
                chInfoReplaceNow.addEventListener("click", clickEvent);
                function clickEvent() {
                    let s = JSON.stringify({"id": chInfoChId.value, "new_id": chInfoReplaceInput.value})
                    fetch("api/replace-id", {
                        method: "POST",
                        body: s
                    })
                    .then(response => {
                        response.json().then(function(d) {
                            if( d["success"] === true ) {
                                var k = i["result"][0];
                                chInfoChId.value = chInfoReplaceInput.value;
                                chInfoChName.value = k["name"];
                                if( k.hasOwnProperty("callSign") ) {
                                    chInfoChCallSign.hidden = false;
                                    chInfoChCallSignLabel.hidden = false;
                                    chInfoChCallSign.value = k["callSign"];
                                } else {
                                    chInfoChCallSign.hidden = true;
                                    chInfoChCallSignLabel.hidden = true;
                                    chInfoChCallSign.value = "";
                                };
                                chInfoImage.setAttribute("src", k["preferredImage"]["uri"]);
                                showNotiMessage("The channel has been replaced!", "success");
                                loadChannelList();
                                chInfoReplaceNow.removeEventListener("click", clickEvent);
                                chInfoReplaceNow.disabled = true;
                            } else {
                                showNotiMessage(d["message"], "error");
                            };
                        });
                    })
                    .catch(error => {
                        console.log(error);
                        showNotiMessage("An error occurred while serving the request.", "error");
                    });
                };
            } else {
                chInfoReplaceResult.value = "(not found)"
            };
        });
    })
    .catch(error => {
        console.log(error);
        showNotiMessage("An error occurred while serving the request.", "error");
    });
};

chInfoChIdSave.addEventListener("click", function() {
    addTvgId(chInfoChId.value, chInfoChIdInput.value);
});

function addTvgId(channelId, tvgId) {
    let s = JSON.stringify({"id": channelId, "tvg-id": tvgId});
    fetch("api/add-tvgid", {
        method: "POST",
        body: s
    })
    .then(response => {
        response.json().then(function(d) {
            if( d["success"] === true ) {
                showNotiMessage("The EPG ID has been saved!", "success");
                loadChannelList();
                loadSettings(mappingTable.getElementsByTagName("tbody")[0].scrollTop);
                return true;
            } else {
                showNotiMessage(d["message"], "error");
            };
        });
    })
    .catch(error => {
        console.log(error);
        showNotiMessage("An error occurred while serving the request.", "error");
    });
};

chRemove.addEventListener("click", function() {
    let s = JSON.stringify({"ids": [chInfoChId.value]});
    fetch("api/remove", {
        method: "POST",
        body: s
    })
    .then(response => {
        response.json().then(function(d) {
            if( d["success"] === true ) {
                showNotiMessage("'" + chInfoChName.value + "' has been removed!", "success");                
                loadChannelList();
                chInfoWindow.classList.add("nav-bar-move");
                blockPage.style.display = "none";
                mainBtnGroup.style.display = "inline";
                setTimeout(function() {
                    chInfoWindow.style.display = "none"; 
                    blockPage.classList.remove("add-blocker"); 
                    chInfoWindow.classList.remove("nav-bar-move");
                    loadSettings(mappingTable.getElementsByTagName("tbody")[0].scrollTop);
                }, 600);
            } else {
                showNotiMessage(d["message"], "error");
            };
        });
    })
    .catch(error => {
        console.log(error);
        showNotiMessage("An error occurred while serving the request.", "error");
    });
});

var countryDefaults = {"BLZ": "BZ", "COL": "CO", "GUY": "GY", "HND": "HN", "PAN": "PA", "AIA": "AI-2640", "ATG": "AG", "ABW": "AW", "BHS": "BS", "BES": "BQ", "CUW": "CW", "DMA": "DM", "GRD": "GD", "MAF": "97150", "KNA": "KN", "LCA": "LC", "TTO": "TT", "TCA": "TKCA1ZZ"}

regionSelection.addEventListener("change", function() {
    var selectedRegion = regionSelection.options[regionSelection.selectedIndex].getAttribute("id");
    var availableCountries = document.getElementsByClassName(selectedRegion);
    for( var i = 1; i < allCountries.length; i++ ) {
        allCountries[i].setAttribute("hidden", true);
    };
    for( var i = 0; i < availableCountries.length; i++ ) {
        availableCountries[i].removeAttribute("hidden");
    };
    if( selectedRegion != "r_none" ) {
        countrySelection.disabled = false;
    } else {
        countrySelection.disabled = true;
    };
    defaultCountry.selected = "selected";
    defaultLineup.selected = "selected";
    postalCode.disabled = true;
    postalCode.value = "";
    providerTypeSelection.disabled = true;
    allLineups.disabled = true;
});

countrySelection.addEventListener("change", function() {
    var selectedCountry = countrySelection.options[countrySelection.selectedIndex].getAttribute("id");
    if( selectedCountry != "c_none" ) {
        if( selectedCountry.toUpperCase() in countryDefaults ) {
            postalCode.value = countryDefaults[selectedCountry.toUpperCase()];
            doneTypingPostalCode();
        } else {
            postalCode.disabled = false;
        };
    } else {
        postalCode.disabled = true;
    };
    postalCode.value = "";
    providerTypeSelection.disabled = true;
    allLineups.disabled = true;
    defaultLineup.selected = "selected";
});

postalCode.addEventListener("keyup", function() {
    clearTimeout(typingTimer);
    if (postalCode.value) {
        typingTimer = setTimeout(doneTypingPostalCode, doneTypingInterval);
    };
});

allLineups.addEventListener("change", function() {
    var selectedLineup = allLineups.options[allLineups.selectedIndex].getAttribute("id");
    if( selectedLineup != "l_none" ) {
        loadLineupChannels(selectedLineup);
    } else {
        tableSection.classList.add("hide-window");
        setTimeout(function() {
            tableSection.style.display = "none";
            tableSection.classList.remove("hide-window");
            loadChannelList();
        }, 200);
    };
});

providerTypeSelection.addEventListener("change", function() {
    var cookieValue = JSON.stringify({"Region": regionSelection.options[regionSelection.selectedIndex].getAttribute("id"), "Country": countrySelection.options[countrySelection.selectedIndex].getAttribute("id"), "PostalCode": postalCode.value, "ServiceType": providerTypeSelection.options[providerTypeSelection.selectedIndex].getAttribute("id")});
    createCookie("LineupFilter", cookieValue, 30);
    var selectedProviderType = providerTypeSelection.options[providerTypeSelection.selectedIndex].getAttribute("id");
    defaultLineup.selected = "selected";
    for( var i = 1; i < allLineups.options.length; i++ ) {
        if( allLineups.options[i].classList.contains(selectedProviderType) || selectedProviderType === "ALL" ) {
            allLineups.options[i].hidden = false;
        } else {
            allLineups.options[i].hidden = true;
        };
    };
});

chSearch.addEventListener('keyup', function() {
    clearTimeout(typingTimer);
    if (chSearch.value) {
        typingTimer = setTimeout(doneTyping, doneTypingInterval);
    };
});

closeResultsWindow.addEventListener('click', function() {
    tableSection.classList.add("hide-window");
    setTimeout(function() {
        searchTable.innerHTML = ""; // TO BE IMPROVED!!!
        tableSection.style.display = "none";
        tableSection.classList.remove("hide-window");
        loadChannelList();
        loadSettings(channelTable.getElementsByTagName("tbody")[0].scrollTop);
    }, 200);
    // loadChannelList();
});

chSearch.addEventListener('search', function() {
    tableSection.classList.add("hide-window");
    setTimeout(function() {
        tableSection.style.display = "none";
        tableSection.classList.remove("hide-window");
        loadChannelList();
    }, 200);
    // loadChannelList();
});

function doneTyping() {
    // searchResultsText.innerText = "Search results";
    let s = JSON.stringify({"value": chSearch.value, "type": chSearchFilter.options[chSearchFilter.selectedIndex].getAttribute("id")});
    
    fetch("api/search", {
        method: "POST",
        body: s
    })
    .then(response => {
        response.json().then(function(d) {
            if( d["success"] === true ) {
                var data = d["result"]
                searchResultsText.innerText = "Search results for '" + chSearch.value + "'";
                for( let i = 0; i < tableClass.length; i++ ) {
                    tableClass[i].style.display = "none";
                };
                searchTable.innerHTML = "";
                for( i in data["hits"] ) {
                    var newRow = searchTable.insertRow();
                    if( data["hits"][i]["station"].hasOwnProperty("preferredImage" ) ) {
                        var imgSrc = '<img src="' + data["hits"][i]["station"]["preferredImage"]["uri"] + '" alt="">'
                    } else {
                        var imgSrc = '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="48" fill="currentColor" class="bi bi-tv" viewBox="0 0 16 16"><path d="M2.5 13.5A.5.5 0 0 1 3 13h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zM13.991 3l.024.001a1.46 1.46 0 0 1 .538.143.757.757 0 0 1 .302.254c.067.1.145.277.145.602v5.991l-.001.024a1.464 1.464 0 0 1-.143.538.758.758 0 0 1-.254.302c-.1.067-.277.145-.602.145H2.009l-.024-.001a1.464 1.464 0 0 1-.538-.143.758.758 0 0 1-.302-.254C1.078 10.502 1 10.325 1 10V4.009l.001-.024a1.46 1.46 0 0 1 .143-.538.758.758 0 0 1 .254-.302C1.498 3.078 1.675 3 2 3h11.991zM14 2H2C0 2 0 4 0 4v6c0 2 2 2 2 2h12c2 0 2-2 2-2V4c0-2-2-2-2-2z"/></svg>'
                    };
                    if( data["hits"][i]["station"]["chExists"] === true ) {
                        var btnShow = '<button disabled id="' + data["hits"][i]["station"]["stationId"] + '" class="added-ch"><svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="currentColor" class="bi bi-check2-circle" viewBox="0 0 16 16"><path d="M2.5 8a5.5 5.5 0 0 1 8.25-4.764.5.5 0 0 0 .5-.866A6.5 6.5 0 1 0 14.5 8a.5.5 0 0 0-1 0 5.5 5.5 0 1 1-11 0z"/><path d="M15.354 3.354a.5.5 0 0 0-.708-.708L8 9.293 5.354 6.646a.5.5 0 1 0-.708.708l3 3a.5.5 0 0 0 .708 0l7-7z"/></svg></button>';
                    } else {
                        var btnShow = '<button id="' + data["hits"][i]["station"]["stationId"] + '" class="add-ch"><svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="currentColor" class="bi bi-plus-circle" viewBox="0 0 16 16"><path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/><path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/></svg></button>';
                    };
                    newRow.innerHTML = '<td>' + imgSrc + '</td><td>' + data["hits"][i]["station"]["name"] + '<p>ID: ' + data["hits"][i]["station"]["stationId"] + ' | ' + data["hits"][i]["station"]["callSign"] + ' | ' + data["hits"][i]["station"]["bcastLangs"][0] + ' | ' + data["hits"][i]["station"]["type"] + '</p></td><td>' + btnShow + '</td>'
                    document.getElementById(data["hits"][i]["station"]["stationId"]).addEventListener("click", function() {
                        addNewChannel(this.getAttribute("id"), false);
                    });
                }
                if( document.getElementById("search-table").rows.length === 0 ) {
                    showNotiMessage("No channels found.", "error");
                    tableSection.classList.add("hide-window");
                    setTimeout(function() {
                        tableSection.style.display = "none";
                        tableSection.classList.remove("hide-window");
                        loadChannelList();
                        loadSettings(channelTable.getElementsByTagName("tbody")[0].scrollTop);
                    }, 200);
                } else {
                    // HEADER
                    tableSection.style.display = "block";
                };
            } else {
                showNotiMessage(d["message"], "error");
            };
        });
    })
    .catch(error => {
        console.log(error);
        showNotiMessage("An error occurred while serving the request.", "error");
    });
};

function doneTypingPostalCode() {
    var selectedCountry = countrySelection.options[countrySelection.selectedIndex].getAttribute("id");
    fetch("api/lineups", {
        method: "POST",
        body: JSON.stringify({"country": selectedCountry, "code": postalCode.value})
    })
    .then(response => {
        response.json().then(function(d) {
            var i, L = allLineups.options.length - 1;
            defaultLineup.selected = "selected";
            for(i = L; i >= 1; i--) {
                allLineups.remove(i);
            };
            if( d["success"] === true ) {
                var cookieValue = JSON.stringify({"Region": regionSelection.options[regionSelection.selectedIndex].getAttribute("id"), "Country": countrySelection.options[countrySelection.selectedIndex].getAttribute("id"), "PostalCode": postalCode.value, "ServiceType": providerTypeSelection.options[providerTypeSelection.selectedIndex].getAttribute("id")});
                createCookie("LineupFilter", cookieValue, 30);
                var data = d["result"]
                var selectedProviderType = providerTypeSelection.options[providerTypeSelection.selectedIndex].getAttribute("id");
                for( i in data ) {
                    var opt = document.createElement('option');
                    opt.id = data[i]["lineupId"];
                    opt.classList.add(data[i]["type"]);
                    opt.innerHTML = data[i]["name"];
                    if( selectedProviderType != data[i]["type"] && selectedProviderType != "ALL" ) {
                        opt.hidden = true;
                    };
                    allLineups.appendChild(opt);
                };
                allLineups.disabled = false;
                providerTypeSelection.disabled = false;
            } else if( d["success"] === false ) {
                showNotiMessage(d["message"], "error");
            };
        });
    })
    .catch(error => {
        console.log(error);
        showNotiMessage("An error occurred while serving the request.", "error");
    });
};

function loadExtLineupChannels(value) {
    if( value.includes("xml") ) {
        var selectedLineup = xmlSelection.options[xmlSelection.options.selectedIndex].textContent;
        loadXmlBtn.textContent = "Loading...";
        loadXmlBtn.disabled = true;
        xmlSelection.disabled = true;
        removeXmlBtn.disabled = true;
    } else {
        var selectedLineup = webSelection.options[webSelection.options.selectedIndex].textContent;
    };

    fetch("api/xmltv_lineup_channels", {
        method: "POST",
        body: JSON.stringify({"id": value})
    })
    .then(response => {
        response.json().then(function(d) {
            if( d["success"] === true ) {
                loadXmlBtn.textContent = "Load channels";
                loadXmlBtn.disabled = false;
                xmlSelection.disabled = false;
                removeXmlBtn.disabled = false;
                blockPage.style.display = "none";
                if( openXmlWindow.classList.contains("selected-btn") ) {
                    xmlWindow.classList.add("nav-bar-move");
                    blockPage.removeEventListener("click", closeXmlWindowEvent);
                    setTimeout(function() {xmlWindow.style.display = "none"; blockPage.classList.remove("add-blocker"); xmlWindow.classList.remove("nav-bar-move")}, 600);
                };
                if( openWebWindow.classList.contains("selected-btn") ) {
                    webWindow.classList.add("nav-bar-move");
                    blockPage.removeEventListener("click", closeWebWindowEvent);
                    setTimeout(function() {webWindow.style.display = "none"; blockPage.classList.remove("add-blocker"); webWindow.classList.remove("nav-bar-move")}, 600);
                };
                mainBtnGroup.style.display = "inline";
                prTypeBtnGroup.style.display = "none";
                openSearch.style.display = "none";
                closeResultsWindow.style.display = "none";
                var data = d["result"]
                for( let i = 0; i < tableClass.length; i++ ) {
                    tableClass[i].style.display = "none";
                };
                searchTable.innerHTML = "";

                var j = [];
                for( k in data ) {
                    j.push(data[k]["name"] + "|" + k);
                };
                j.sort((a, b) => a.localeCompare(b, undefined, {sensitivity: 'base'}));

                for( var b = 0; b < j.length; b++ ) {
                    i = j[b].split("|")[1];
                    var newRow = searchTable.insertRow();
                    newRow.id = "mn|" + value + "|" + i;
                    newRow.classList.add("mn_row");
                    if( data[i].hasOwnProperty("icon") ) {
                        if( data[i]["icon"] == null || data[i]["icon"] == "" ) {
                            var imgSrc = '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="48" fill="currentColor" class="bi bi-tv" viewBox="0 0 16 16"><path d="M2.5 13.5A.5.5 0 0 1 3 13h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zM13.991 3l.024.001a1.46 1.46 0 0 1 .538.143.757.757 0 0 1 .302.254c.067.1.145.277.145.602v5.991l-.001.024a1.464 1.464 0 0 1-.143.538.758.758 0 0 1-.254.302c-.1.067-.277.145-.602.145H2.009l-.024-.001a1.464 1.464 0 0 1-.538-.143.758.758 0 0 1-.302-.254C1.078 10.502 1 10.325 1 10V4.009l.001-.024a1.46 1.46 0 0 1 .143-.538.758.758 0 0 1 .254-.302C1.498 3.078 1.675 3 2 3h11.991zM14 2H2C0 2 0 4 0 4v6c0 2 2 2 2 2h12c2 0 2-2 2-2V4c0-2-2-2-2-2z"/></svg>';
                        } else {
                            var imgSrc = '<img src="' + data[i]["icon"] + '" alt="">';
                        };
                    } else {
                        var imgSrc = '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="48" fill="currentColor" class="bi bi-tv" viewBox="0 0 16 16"><path d="M2.5 13.5A.5.5 0 0 1 3 13h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zM13.991 3l.024.001a1.46 1.46 0 0 1 .538.143.757.757 0 0 1 .302.254c.067.1.145.277.145.602v5.991l-.001.024a1.464 1.464 0 0 1-.143.538.758.758 0 0 1-.254.302c-.1.067-.277.145-.602.145H2.009l-.024-.001a1.464 1.464 0 0 1-.538-.143.758.758 0 0 1-.302-.254C1.078 10.502 1 10.325 1 10V4.009l.001-.024a1.46 1.46 0 0 1 .143-.538.758.758 0 0 1 .254-.302C1.498 3.078 1.675 3 2 3h11.991zM14 2H2C0 2 0 4 0 4v6c0 2 2 2 2 2h12c2 0 2-2 2-2V4c0-2-2-2-2-2z"/></svg>'
                    };
                    if( data[i]["chExists"] === true ) {
                        var btnShow = '<button disabled id="' + i + '" class="added-ch"><svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="currentColor" class="bi bi-check2-circle" viewBox="0 0 16 16"><path d="M2.5 8a5.5 5.5 0 0 1 8.25-4.764.5.5 0 0 0 .5-.866A6.5 6.5 0 1 0 14.5 8a.5.5 0 0 0-1 0 5.5 5.5 0 1 1-11 0z"/><path d="M15.354 3.354a.5.5 0 0 0-.708-.708L8 9.293 5.354 6.646a.5.5 0 1 0-.708.708l3 3a.5.5 0 0 0 .708 0l7-7z"/></svg></button>';
                        newRow.classList.remove("mn_row");
                    } else {
                        var btnShow = '<button id="' + i + '" class="add-ch"><svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="currentColor" class="bi bi-plus-circle" viewBox="0 0 16 16"><path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/><path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/></svg></button>';
                    };
                    newRow.innerHTML = '<td>' + imgSrc + '</td><td>' + data[i]["name"] + '<p>ID: ' + i + '</p></td><td>' + btnShow + '</td>'
                    document.getElementById(i).addEventListener("click", function() {
                        addNewChannel(value + "|" + this.getAttribute("id"), true);
                    });                    
                };

                if( document.getElementById("search-table").rows.length === 0 ) {
                    // HEADER
                    tableSection.classList.add("hide-window");
                    setTimeout(function() {
                         tableSection.style.display = "none";
                         tableSection.classList.remove("hide-window");
                         loadChannelList();
                     }, 200);
                 } else {
                     // HEADER
                     tableSection.style.display = "block";
                 };

                 var channelRows = document.getElementsByClassName("mn_row");
                 var channelInfoElements = document.getElementsByClassName("add-ch");

                 for( let c = 0; c < channelRows.length; c++ ) {
                     var td = channelRows[c].getElementsByTagName("td");
                     for( let r = 0; r < 2; r++ ) {
                         td[r].addEventListener("click", function() {
                             if( channelRows[c].classList.contains("ch_selected") ) {
                                 channelRows[c].classList.remove("ch_selected");    
                             } else if ( !channelRows[c].classList.contains("mn_added") ) {
                                 channelRows[c].classList.add("ch_selected");
                             };
                             var multiSelectMode = false
                             for( let d = 0; d < channelRows.length; d++ ) {
                                 if( channelRows[d].classList.contains("ch_selected") ) {
                                     multiSelectMode = true;
                                 };
                             };
                             if( multiSelectMode === true ) {
                                 mainBtnGroup.style.display = "none";
                                 chLpMultiSelectBtnGroup.style.display = "inline";
                                 for( let d = 0; d < channelInfoElements.length; d++ ) {
                                     if( !channelRows[d].classList.contains("mn_added") ) {
                                         channelInfoElements[d].disabled = true;
                                         channelInfoElements[d].classList.add("add-ch-disabled");
                                     };
                                 };
                             } else {
                                 mainBtnGroup.style.display = "inline";
                                 chLpMultiSelectBtnGroup.style.display = "none";
                                 for( let d = 0; d < channelInfoElements.length; d++ ) {
                                     if( !channelRows[d].classList.contains("mn_added") ) {
                                         channelInfoElements[d].disabled = false;
                                         channelInfoElements[d].classList.remove("add-ch-disabled");
                                     };
                                 };
                             };
                         });
                     };
                 };
                searchResultsText.innerText = "Lineup: " + selectedLineup;
                openSearch.style.display = "inline";
                closeResultsWindow.style.display = "inline";
            } else {
                if( value.includes("xml") ) {
                    loadXmlBtn.textContent = "Load channels";
                    loadXmlBtn.disabled = false;
                    xmlSelection.disabled = false;
                    removeXmlBtn.disabled = false;
                };
                var selectedLineupString = webSelection.options[webSelection.options.selectedIndex].textContent;
                if( selectedLineupString.includes("🔑") ) {
                    if ( d["message"].includes("credentials") ) {
                        showNotiMessage("Please insert/check your credentials.");
                    } else {
                        showNotiMessage(d["message"], "error");
                    };
                    webUser.disabled = false;
                    webPw.disabled = false;
                } else {
                    webSelection.options[0].selected = 'selected';
                    showNotiMessage("An error occurred while loading the channel list.", "error");
                };
            };
        })
    })
};

function loadLineupChannels(value) {
    // searchResultsText.innerText = "Search results";
    var selectedLineup = allLineups.options[allLineups.selectedIndex].textContent;
    fetch("api/lineup_channels", {
        method: "POST",
        body: JSON.stringify({"id": value})
    })
    .then(response => {
        response.json().then(function(d) {
            if( d["success"] === true ) {
                searchWindow.classList.add("nav-bar-move");
                blockPage.style.display = "none";
                blockPage.removeEventListener("click", closeSearchWindowEvent);
                mainBtnGroup.style.display = "inline";
                prTypeBtnGroup.style.display = "none";
                setTimeout(function() {searchWindow.style.display = "none"; blockPage.classList.remove("add-blocker"); searchWindow.classList.remove("nav-bar-move")}, 600);
                openSearch.style.display = "none";
                closeResultsWindow.style.display = "none";
                var data = d["result"]
                for( let i = 0; i < tableClass.length; i++ ) {
                    tableClass[i].style.display = "none";
                };
                searchTable.innerHTML = "";

                var j = [];
                for( k in data ) {
                    j.push(data[k]["callSign"] + "_" + data[k]["stationId"]);
                };
                j.sort((a, b) => a.localeCompare(b, undefined, {sensitivity: 'base'}));

                for( var b = 0; b < j.length; b++ ) {
                    i = j[b].split("_")[1];
                    var newRow = searchTable.insertRow();
                    newRow.id = "mn|" + data[i]["stationId"];
                    newRow.classList.add("mn_row");
                    if( data[i].hasOwnProperty("preferredImage") ) {
                        var imgSrc = '<img src="' + data[i]["preferredImage"]["uri"] + '" alt="">';
                    } else {
                        var imgSrc = '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="48" fill="currentColor" class="bi bi-tv" viewBox="0 0 16 16"><path d="M2.5 13.5A.5.5 0 0 1 3 13h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zM13.991 3l.024.001a1.46 1.46 0 0 1 .538.143.757.757 0 0 1 .302.254c.067.1.145.277.145.602v5.991l-.001.024a1.464 1.464 0 0 1-.143.538.758.758 0 0 1-.254.302c-.1.067-.277.145-.602.145H2.009l-.024-.001a1.464 1.464 0 0 1-.538-.143.758.758 0 0 1-.302-.254C1.078 10.502 1 10.325 1 10V4.009l.001-.024a1.46 1.46 0 0 1 .143-.538.758.758 0 0 1 .254-.302C1.498 3.078 1.675 3 2 3h11.991zM14 2H2C0 2 0 4 0 4v6c0 2 2 2 2 2h12c2 0 2-2 2-2V4c0-2-2-2-2-2z"/></svg>'
                    };
                    newRow.innerHTML = '<td disabled>' + imgSrc + '</td><td class="callsign">' + data[i]["callSign"] + '<p>ID: ' + data[i]["stationId"] + '</p></td><td></td>'
                };

                if( document.getElementById("search-table").rows.length === 0 ) {
                   // HEADER
                   tableSection.classList.add("hide-window");
                   setTimeout(function() {
                        tableSection.style.display = "none";
                        tableSection.classList.remove("hide-window");
                        loadChannelList();
                    }, 200);
                } else {
                    // HEADER
                    tableSection.style.display = "block";
                };
                
                searchResultsText.innerText = "Fetching TMS lineup channel details...";

                for( let c = 0; c < j.length; c++ ) {
                    b = j[c].split("_")[1];
                    fetch("api/channel_info", {
                        method: "POST",
                        body: JSON.stringify({"id": data[b]["stationId"]})
                    })
                    .then(response => {
                        response.json().then(function(i) {
                            if( i["success"] === true ) {
                                var info = i["result"]
                                if( info[0].hasOwnProperty("preferredImage") ) {
                                    var imgSrc = '<img src="' + info[0]["preferredImage"]["uri"] + '" alt="">';
                                } else {
                                    var imgSrc = '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="48" fill="currentColor" class="bi bi-tv" viewBox="0 0 16 16"><path d="M2.5 13.5A.5.5 0 0 1 3 13h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zM13.991 3l.024.001a1.46 1.46 0 0 1 .538.143.757.757 0 0 1 .302.254c.067.1.145.277.145.602v5.991l-.001.024a1.464 1.464 0 0 1-.143.538.758.758 0 0 1-.254.302c-.1.067-.277.145-.602.145H2.009l-.024-.001a1.464 1.464 0 0 1-.538-.143.758.758 0 0 1-.302-.254C1.078 10.502 1 10.325 1 10V4.009l.001-.024a1.46 1.46 0 0 1 .143-.538.758.758 0 0 1 .254-.302C1.498 3.078 1.675 3 2 3h11.991zM14 2H2C0 2 0 4 0 4v6c0 2 2 2 2 2h12c2 0 2-2 2-2V4c0-2-2-2-2-2z"/></svg>'
                                };
                                if( info[0]["chExists"] === true ) {
                                    var btnShow = '<button disabled id="' + info[0]["stationId"] + '" class="added-ch"><svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="currentColor" class="bi bi-check2-circle" viewBox="0 0 16 16"><path d="M2.5 8a5.5 5.5 0 0 1 8.25-4.764.5.5 0 0 0 .5-.866A6.5 6.5 0 1 0 14.5 8a.5.5 0 0 0-1 0 5.5 5.5 0 1 1-11 0z"/><path d="M15.354 3.354a.5.5 0 0 0-.708-.708L8 9.293 5.354 6.646a.5.5 0 1 0-.708.708l3 3a.5.5 0 0 0 .708 0l7-7z"/></svg></button>';
                                    document.getElementById("mn|" + info[0]["stationId"]).classList.remove("mn_row");
                                } else {
                                    var btnShow = '<button id="' + info[0]["stationId"] + '" class="add-ch"><svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="currentColor" class="bi bi-plus-circle" viewBox="0 0 16 16"><path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/><path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/></svg></button>';
                                };
                                document.getElementById("mn|" + info[0]["stationId"]).innerHTML = '<td>' + imgSrc + '</td><td>' + info[0]["name"] + '<p>ID: ' + info[0]["stationId"] + ' | ' + info[0]["callSign"] + ' | ' + info[0]["bcastLangs"][0] + ' | ' + info[0]["type"] + '</p></td><td>' + btnShow + '</td>'
                                document.getElementById(info[0]["stationId"]).addEventListener("click", function() {
                                    addNewChannel(this.getAttribute("id"), true);
                                });

                                if( (j.length - c) === 1 ) {
                                    var channelRows = document.getElementsByClassName("mn_row");
                                    var channelInfoElements = document.getElementsByClassName("add-ch");

                                    for( let c = 0; c < channelRows.length; c++ ) {
                                        var td = channelRows[c].getElementsByTagName("td");
                                        for( let r = 0; r < 2; r++ ) {
                                            td[r].addEventListener("click", function() {
                                                if( channelRows[c].classList.contains("ch_selected") ) {
                                                    channelRows[c].classList.remove("ch_selected");    
                                                } else if ( !channelRows[c].classList.contains("mn_added") ) {
                                                    channelRows[c].classList.add("ch_selected");
                                                };
                                                var multiSelectMode = false
                                                for( let d = 0; d < channelRows.length; d++ ) {
                                                    if( channelRows[d].classList.contains("ch_selected") ) {
                                                        multiSelectMode = true;
                                                    };
                                                };
                                                if( multiSelectMode === true ) {
                                                    mainBtnGroup.style.display = "none";
                                                    chLpMultiSelectBtnGroup.style.display = "inline";
                                                    for( let d = 0; d < channelInfoElements.length; d++ ) {
                                                        if( !channelRows[d].classList.contains("mn_added") ) {
                                                            channelInfoElements[d].disabled = true;
                                                            channelInfoElements[d].classList.add("add-ch-disabled");
                                                        };
                                                    };
                                                } else {
                                                    mainBtnGroup.style.display = "inline";
                                                    chLpMultiSelectBtnGroup.style.display = "none";
                                                    for( let d = 0; d < channelInfoElements.length; d++ ) {
                                                        if( !channelRows[d].classList.contains("mn_added") ) {
                                                            channelInfoElements[d].disabled = false;
                                                            channelInfoElements[d].classList.remove("add-ch-disabled");
                                                        };
                                                    };
                                                };
                                            });
                                        };
                                    };
                                    searchResultsText.innerText = "TMS Lineup: " + selectedLineup;
                                    openSearch.style.display = "inline";
                                    closeResultsWindow.style.display = "inline";
                                    showNotiMessage("All lineup channels fetched. Multi-selection enabled.");
                                };                            
                            };
                        });
                    })
                    .catch(error => {
                        console.log(error);
                        showNotiMessage("An error occurred while serving the request.", "error");
                    });
                };
            } else {
                showNotiMessage(d["message"], "error");
            };
        });
    })
    .catch(error => {
        console.log(error);
        showNotiMessage("An error occurred while serving the request.", "error");
    });
};

function addNewChannel(value, lineup) {
    fetch("api/add", {
        method: "POST",
        body: JSON.stringify({"ids": [value]})
    })
    .then(response => {
        response.json().then(function(data) {
            if( data["success"] === true ) {
                if( value.includes("|") ) {
                    var v = value.split("|")[1];
                } else {
                    var v = value;
                };
                document.getElementById(v).classList.add("added-ch");
                document.getElementById(v).disabled = true;
                if( lineup === true ) {
                    document.getElementById("mn|" + value).classList.add("mn_added");
                };
                document.getElementById(v).innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="currentColor" class="bi bi-check2-circle" viewBox="0 0 16 16"><path d="M2.5 8a5.5 5.5 0 0 1 8.25-4.764.5.5 0 0 0 .5-.866A6.5 6.5 0 1 0 14.5 8a.5.5 0 0 0-1 0 5.5 5.5 0 1 1-11 0z"/><path d="M15.354 3.354a.5.5 0 0 0-.708-.708L8 9.293 5.354 6.646a.5.5 0 1 0-.708.708l3 3a.5.5 0 0 0 .708 0l7-7z"/></svg>';

                showNotiMessage("New channel added!", "success");
            } else {
                showNotiMessage(data["message"], "error");
            };
        });
    })
    .catch(error => {
        console.log(error);
        showNotiMessage("An error occurred while serving the request.", "error");
    });
};

function loadChannelList() {
    fetch("api/listings" ,{
        method: "GET"
    })
    .then(response => {
        response.json().then(function(data) {
            var j = [];
            for( k in data ) {
                j.push(data[k]["name"] + "|" + k);
            };
            j.sort((a, b) => a.localeCompare(b, undefined, {sensitivity: 'base'}));

            if( channelTable.getElementsByTagName("td").length > 0 ) {
                var scrollPosition = channelTable.getElementsByTagName("tbody")[0].scrollTop;
            } else {
                var scrollPosition = 0;
            };

            channelTable.innerHTML = "";
            chSearchBar.value = "";

            if( j.length === 0 ) {
                for( let i = 0; i < chInSetup.length; i++ ) {
                    chInSetup[i].style.display = "none";
                };
                noChInSetup.style.display = "block";
            } else {
                for( let i = 0; i < chInSetup.length; i++ ) {
                    chInSetup[i].style.display = "block";
                };
                noChInSetup.style.display = "none";
            };

            for( k in j ) {                
                c_id = j[k].split("|").pop();
                var newRow = channelTable.insertRow();
                newRow.setAttribute("id", "ch_" + c_id);
                newRow.classList.add("ch_row");
                if( data[c_id].hasOwnProperty("tvg-id") ) {
                    var tvg = '<p class="id-show">EPG-ID: ' + data[c_id]["tvg-id"] + '</p>';
                } else {
                    var tvg = "";
                };
                if( data[c_id].hasOwnProperty("preferredImage" ) ) {
                    if( data[c_id]["preferredImage"]["uri"] == null || data[c_id]["preferredImage"]["uri"] == "" ) {
                        var imgSrc = '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="48" fill="currentColor" class="bi bi-tv" viewBox="0 0 16 16"><path d="M2.5 13.5A.5.5 0 0 1 3 13h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zM13.991 3l.024.001a1.46 1.46 0 0 1 .538.143.757.757 0 0 1 .302.254c.067.1.145.277.145.602v5.991l-.001.024a1.464 1.464 0 0 1-.143.538.758.758 0 0 1-.254.302c-.1.067-.277.145-.602.145H2.009l-.024-.001a1.464 1.464 0 0 1-.538-.143.758.758 0 0 1-.302-.254C1.078 10.502 1 10.325 1 10V4.009l.001-.024a1.46 1.46 0 0 1 .143-.538.758.758 0 0 1 .254-.302C1.498 3.078 1.675 3 2 3h11.991zM14 2H2C0 2 0 4 0 4v6c0 2 2 2 2 2h12c2 0 2-2 2-2V4c0-2-2-2-2-2z"/></svg>';
                    } else {
                        var imgSrc = '<img src="' + data[c_id]["preferredImage"]["uri"] + '" alt="">'
                    };
                } else {
                    var imgSrc = '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="48" fill="currentColor" class="bi bi-tv" viewBox="0 0 16 16"><path d="M2.5 13.5A.5.5 0 0 1 3 13h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zM13.991 3l.024.001a1.46 1.46 0 0 1 .538.143.757.757 0 0 1 .302.254c.067.1.145.277.145.602v5.991l-.001.024a1.464 1.464 0 0 1-.143.538.758.758 0 0 1-.254.302c-.1.067-.277.145-.602.145H2.009l-.024-.001a1.464 1.464 0 0 1-.538-.143.758.758 0 0 1-.302-.254C1.078 10.502 1 10.325 1 10V4.009l.001-.024a1.46 1.46 0 0 1 .143-.538.758.758 0 0 1 .254-.302C1.498 3.078 1.675 3 2 3h11.991zM14 2H2C0 2 0 4 0 4v6c0 2 2 2 2 2h12c2 0 2-2 2-2V4c0-2-2-2-2-2z"/></svg>'
                };
                if( data[c_id].hasOwnProperty("bcastLangs") ) {
                    var bcastLangs = data[c_id]["bcastLangs"][0];
                } else {
                    var bcastLangs = undefined;
                };

                if( bcastLangs === undefined && data[c_id]["callSign"] === undefined && data[c_id]["type"] === undefined ) {
                    newRow.innerHTML = '<td>' + imgSrc + '</td><td>' + data[c_id]["name"] + tvg + '<p>ID: ' + c_id + '</p></td><td><button id="' + c_id + '" class="info-ch"><svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="currentColor" class="bi bi-info-circle" viewBox="0 0 16 16"><path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/><path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5v11z"/></svg></button></td>'
                } else {
                    newRow.innerHTML = '<td>' + imgSrc + '</td><td>' + data[c_id]["name"] + tvg + '<p>ID: ' + c_id + ' | ' + data[c_id]["callSign"] + ' | ' + bcastLangs + ' | ' + data[c_id]["type"] + '</p></td><td><button id="' + data[c_id]["stationId"] + '" class="info-ch"><svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="currentColor" class="bi bi-info-circle" viewBox="0 0 16 16"><path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/><path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5v11z"/></svg></button></td>'
                };
            };
            channelSection.style.display = "block";
            if( channelTable.getElementsByTagName("td").length > 0 ) {
                channelTable.getElementsByTagName("tbody")[0].scrollTop = scrollPosition;
            };
         
            var channelRows = document.getElementsByClassName("ch_row");
            var channelInfoElements = document.getElementsByClassName("info-ch");

            for( let i = 0; i < channelRows.length; i++ ) {
                var td = channelRows[i].getElementsByTagName("td");
                for( let b = 0; b < 2; b++ ) {
                    td[b].addEventListener("click", function() {
                        if( channelRows[i].classList.contains("ch_selected") ) {
                            channelRows[i].classList.remove("ch_selected");    
                        } else {
                            channelRows[i].classList.add("ch_selected");
                        };
                        var multiSelectMode = false
                        for( let c = 0; c < channelRows.length; c++ ) {
                            if( channelRows[c].classList.contains("ch_selected") ) {
                                multiSelectMode = true;
                            };
                        };
                        if( multiSelectMode === true ) {
                            if( document.getElementsByClassName("mp_selected").length === 1 ) {
                                chMap.disabled = false;
                            } else {
                                chMap.disabled = true;
                            };
                            mainBtnGroup.style.display = "none";
                            chMultiSelectBtnGroup.style.display = "inline";
                            for( let i = 0; i < channelInfoElements.length; i++ ) {
                                channelInfoElements[i].disabled = true;
                                channelInfoElements[i].classList.add("info-ch-disabled");
                            };
                        } else {
                            mainBtnGroup.style.display = "inline";
                            chMultiSelectBtnGroup.style.display = "none";
                            for( let i = 0; i < channelInfoElements.length; i++ ) {
                                channelInfoElements[i].disabled = false;
                                channelInfoElements[i].classList.remove("info-ch-disabled");
                            };
                        };
                    });
                };
            };

            for( let i = 0; i < channelInfoElements.length; i++ ) {
                channelInfoElements[i].addEventListener("click", function() {
                    mainBtnGroup.style.display = "none";
                    var k = channelInfoElements[i].getAttribute("id");
                    chInfoImage.style.visibility = "visible";
                    if( data[k].hasOwnProperty("preferredImage") ) {
                        if( data[k]["preferredImage"]["uri"] == null ) {
                            chInfoImage.style.visibility = "hidden";
                        } else {
                            chInfoImage.setAttribute("src", data[k]["preferredImage"]["uri"]);
                        };
                    } else {
                        chInfoImage.setAttribute("src", "");
                    };
                    chInfoChName.value = data[k]["name"];
                    if( data[k].hasOwnProperty("callSign") ) {
                        chInfoChCallSign.hidden = false;
                        chInfoChCallSignLabel.hidden = false;
                        chInfoChCallSign.value = data[k]["callSign"];
                    } else {
                        chInfoChCallSign.hidden = true;
                        chInfoChCallSignLabel.hidden = true;
                        chInfoChCallSign.value = "";
                    };
                    chInfoChId.value = k;
                    chInfoWindow.style.display = "inline";
                    blockPage.classList.add("add-blocker");
                    blockPage.style.display = "inline";
                    blockPage.addEventListener("click", closeChInfoWindowEvent);
                    if( data[k].hasOwnProperty("tvg-id") ) {
                        chInfoChIdInput.value = data[k]["tvg-id"];
                    } else {
                        chInfoChIdInput.value = "";
                    };
                    chInfoChIdResult.value = "";
                    chInfoChIdSave.disabled = true;
                });
            };
        });
    })
    .catch(error => {
        console.log(error);
        showNotiMessage("An error occurred while serving the request.", "error");
    });
};


// External code

var createCookie = function(name, value, days) {
    var expires;
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toGMTString();
    }
    else {
        expires = "";
    }
    document.cookie = name + "=" + value + expires + "; path=/";
}

function getCookie(c_name) {
    if (document.cookie.length > 0) {
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1) {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1) {
                c_end = document.cookie.length;
            }
            return unescape(document.cookie.substring(c_start, c_end));
        }
    }
    return "";
}