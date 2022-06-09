wg = window.wireguard.generateKeypair();
document.getElementById("id_public_key").value = wg.publicKey;
document.getElementById("add_peer_private_key").innerText = wg.privateKey;
