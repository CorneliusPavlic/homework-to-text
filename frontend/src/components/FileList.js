import React from 'react';
import FileItem from './FileItem';
import '../styles/FileList.css';
const FileList = ({ uploadedFiles, onDelete, onView }) => {
  return (
<div className="file-list">
  {[...new Map(uploadedFiles.map(item => [item.fileName, item])).values()].map((item, index) => (
    <FileItem
      key={index}
      fileName={item.fileName}
      result={item.result}
      onDelete={() => onDelete(index)}
      onView={() => onView(item.result)}
    />
  ))}
</div>
  );
};

export default FileList;
