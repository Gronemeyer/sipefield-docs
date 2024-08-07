def save_to_bids(path=SAVE_DIR):
    """
    Make a BIDS formatted directory 
    
    Accesses global variables for protocol_id, subject_id, session_id
    
    Organizes the directory structure as follows:
    path/protocol_id-subject_id/ses-session_id/anat
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S') # get current timestamp
    anat_dir = os.path.join(path, f"{protocol_id}-{subject_id}", f"ses-{session_id}", "anat")
    os.makedirs(anat_dir, exist_ok=True) # create the directory if it doesn't exist
    filename = os.path.join(anat_dir, f"sub-{subject_id}_ses-{session_id}_{timestamp}.tiff")
    return filename # returns the filename
