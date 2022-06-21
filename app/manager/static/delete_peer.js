function deletePeer(id, count) {
    let message = "Are you sure, that you'd like to delete this peer?";
    if (count === 1) {
        message += "\nConfirming this action will disconnect you immediately, " +
            "you won't be able to create a new peer without help from the administrators!";
    }
    if (confirm(message)) {
        fetch(`/manage/delete/${id}`);
        location.reload();
    }
}
