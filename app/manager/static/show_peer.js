async function show_peer(id) {
    let response = await fetch(`/manage/api/show/${id}`);
    let responseBody = await response.json();

    let showPeerBody = document.getElementById('showPeerBody');
    if (response.status === 200 && 'peer' in responseBody && 'remote' in responseBody) {
        let showPeerConfig = document.createElement('code');
        showPeerConfig.innerText =
            `# ${responseBody.remote.description}

            [Interface]
            Address = ${responseBody.peer.tunnelIpv4}/32,${responseBody.peer.tunnelIpv6}/128
            PrivateKey = ###### YOUR PRIVATE KEY ######

            [Peer]
            PublicKey = ${responseBody.remote.publicKey}
            Endpoint = ${responseBody.remote.endpoint}
            AllowedIPs = 0.0.0.0/0,::/0
            PersistentKeepalive = 30`;
        showPeerBody.appendChild(showPeerConfig);
    } else {
        let showPeerError = document.createElement('p');
        if (responseBody.error === 'not_found_or_forbidden') {
            showPeerError.innerHTML = "Peer not found or access denied, <a href='..'>go back to the overview</a>!";
        } else {
            showPeerError.innerText = responseBody.error;
        }
        showPeerBody.appendChild(showPeerError);
    }
}

let splittedUrl = window.location.href.split("/")
show_peer(splittedUrl[splittedUrl.length-1]);
