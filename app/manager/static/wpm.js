const addPeerModal = new bootstrap.Modal(document.getElementById('addPeerModal'), {});
const showConfigModal = new bootstrap.Modal(document.getElementById('showConfigModal'), {});

/**
 * open the bootstrap modal to create a new peer
 */
function openAddPeerModal() {
    // removed const/let/var to enable deletion of the variable after the keys have been extracted.
    wg = window.wireguard.generateKeypair();
    document.getElementById("addPeerModalPublicKey").value = wg.publicKey;
    document.getElementById("addPeerPrivateKey").innerText = wg.privateKey;
    document.getElementById("addPeerModalName").value = "";
    document.getElementById("addPeerModalEnablePSK").checked = false;
    document.getElementById("addPeerModalPSK").value = "";
    addPeerModal.show();
    delete wg
}

/**
 * event to create a new peer
 */
document.getElementById("addPeerButton").addEventListener('click', async e => {
    e.preventDefault();
    const nameInput = document.getElementById("addPeerModalName");
    const publicKey = document.getElementById("addPeerModalPublicKey").value;
    const psk = document.getElementById("addPeerModalPSK").value;
    const addPeerError = document.getElementById("addPeerError");

    const response = await fetch('/manage/add', {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            name: nameInput.value,
            publicKey: publicKey,
            psk: psk,
        }),
        mode: 'same-origin',  // Do not send CSRF token to another domain.
    });
    if (response.status === 200) {
        // reload table when peer has been added successfully
        await showPeerTable();
        addPeerModal.hide();
    } else {
        const responseBody = await response.json();
        switch (responseBody.error) {
            case 'invalid_wireguard_public_key':
                addPeerError.innerText = "Invalid Wireguard Public Key!";
                break;
            case 'invalid_wireguard_psk':
                addPeerError.innerText = "Invalid Wireguard PSK!";
                break;
            case 'invalid_peer_name_format':
                addPeerError.innerText = "Invalid Wireguard Peer Name!";
                break;
            case 'peer_name_already_in_use':
                addPeerError.innerText = "Wireguard Peer Name is already in use!";
                break;
            case 'invalid_payload':
                addPeerError.innerText = "Invalid Payload, contact Nico!";
                break;
            default:
                addPeerError.innerText = responseBody.error;
                break;
        }
        addPeerError.style.display = 'block';
    }
});

/**
 * reload the table which contains all your wireguard peers
 */
async function showPeerTable() {
    const wireguardPeers = document.querySelector("tbody");
    // clear table
    wireguardPeers.innerHTML = ""

    const response = await fetch(`/manage/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json',
        },
        mode: 'same-origin',  // Do not send CSRF token to another domain.
    });

    if (response.status === 200) {
        const responseBody = await response.json();
        responseBody.peers.forEach(peer => {
            const row = wireguardPeers.insertRow(-1);

            // name of the peer (required for vyos config, the user can use this name to identify his own peers)
            const peerName = row.insertCell(0);
            peerName.innerText = peer.name;

            // IPv4 and IPv6 addresses which may be used by the client inside the wireguard tunnel.
            const peerIpAddresses = row.insertCell(1);
            peerIpAddresses.innerText = peer.tunnelIpAddresses.join('\n');

            // public key of the clients keypair
            const peerPublicKey = row.insertCell(2);
            peerPublicKey.innerText = peer.publicKey;

            // indicator whether the wireguard peer has been applied on the other side of the tunnel (here: vyos router)
            const peerValid = row.insertCell(3);
            const peerValidCircle = document.createElement("i");
            peerValidCircle.className = "fa-solid fa-circle"
            if (peer.valid) {
                peerValidCircle.title = "Peer is valid and should be working!";
                peerValidCircle.style.color = "#4cb34c";
            } else {
                peerValidCircle.title = "Peer has not been applied yet, please wait!";
                peerValidCircle.style.color = "#e50a0a";
            }
            peerValidCircle["data-bs-toggle"] = "tooltip";
            peerValidCircle["data-bs-placement"] = "top";
            peerValid.appendChild(peerValidCircle);

            // show wireguard config modal button
            const showPeerModal = row.insertCell(4);
            const showPeerModalLink = document.createElement("a");
            showPeerModalLink.href = "javascript:void(0)";
            showPeerModalLink.onclick = () => showPeer(peer.id);
            const showPeerModalLinkIcon = document.createElement("i");
            showPeerModalLinkIcon.className = "fa-solid fa-eye";
            showPeerModalLink.appendChild(showPeerModalLinkIcon);
            showPeerModal.appendChild(showPeerModalLink);

            // delete wireguard peer button
            const deletePeerCell = row.insertCell(5);
            const deletePeerLink = document.createElement("a");
            deletePeerLink.href = "javascript:void(0)";
            deletePeerLink.onclick = () => deletePeer(peer.id, responseBody.peers.length);
            const deletePeerLinkIcon = document.createElement("i");
            deletePeerLinkIcon.className = "fa-solid fa-trash";
            deletePeerLink.appendChild(deletePeerLinkIcon);
            deletePeerCell.appendChild(deletePeerLink);
        });
    }
}

/**
 * show the wireguard configuration for a specific peer, identified by the id
 */
async function showPeer(id) {
    // get data for config
    const response = await fetch(`/manage/show/${id}`);
    const responseBody = await response.json();

    const showPeerBody = document.getElementById('showPeerBody');
    // clear field
    showPeerBody.innerHTML = ""
    // if peer exists and the required information is in the response show wireguard configuration
    if (response.status === 200 && 'peer' in responseBody && 'remote' in responseBody) {
        let showPeerConfig = document.createElement('code');
        let peerConfig = [];
        peerConfig.push(
            `# ${responseBody.remote.description}\n\n`,
            `[Interface]\n`,
            `Address = ${responseBody.peer.tunnelIpAddresses.join(',')}\n`,
            `PrivateKey = ###### YOUR PRIVATE KEY ######\n`,
            `DNS = ${responseBody.remote.dnsServer}\n\n`,
            `[Peer]\n`,
            `PublicKey = ${responseBody.remote.publicKey}\n`,
            `Endpoint = ${responseBody.remote.endpoint}\n`,
            `AllowedIPs = 0.0.0.0/0,::/0\n`,
            `PersistentKeepalive = 30\n`,
        );
        if (responseBody.peer.psk) {
            peerConfig.push(`PresharedKey = ${responseBody.peer.psk}\n`)
        }
        showPeerConfig.innerText = peerConfig.join("");
        showPeerBody.appendChild(showPeerConfig);
    } else {
        // in case of error, handle the error
        let showPeerError = document.createElement('p');
        switch (responseBody.error) {
            case 'not_found_or_forbidden':
                showPeerError.innerHTML = "Peer not found or access denied, <a href='..'>go back to the overview</a>!";
                break;
            default:
                showPeerError.innerText = responseBody.error;
                break;
        }
        showPeerBody.appendChild(showPeerError);
    }
    showConfigModal.show()
}

async function deletePeer(id, count) {
    let message = "Are you sure, that you'd like to delete this peer?";
    if (count === 1) {
        message += "\nConfirming this action will disconnect you immediately, " +
            "you won't be able to create a new peer without help from the administrators!";
    }
    if (!confirm(message)) {
        return;
    }
    const response = await fetch(`/manage/delete/${id}`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json',
        },
        mode: 'same-origin',  // Do not send CSRF token to another domain.
    });
    if (response.status === 201) {
        // reload table
        await showPeerTable()
    }
}

/**
 * When the user checks the switch "Enable PSK", generate the psk and make it visible
 */
document.getElementById("addPeerModalEnablePSK").addEventListener('change', (e) => {
    // generate psk
    // show psk field
    if (e.target.checked) {
        document.getElementById("addPeerModalPSK").value = window.wireguard.generatePSK();
        document.getElementById("addPeerModalPSKOuterElem").style.display = "block";
    } else {
        document.getElementById("addPeerModalPSK").value = "";
        document.getElementById("addPeerModalPSKOuterElem").style.display = "none";
    }
});

/**
 * Load peer table directly after the website has been opened.
 */
showPeerTable().then();
const showPeerTableInterval = setInterval(function() {
    showPeerTable().then();
}, 10000);