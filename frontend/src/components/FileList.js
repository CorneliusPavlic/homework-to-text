import React from 'react';
import FileItem from './FileItem';
import '../styles/FileList.css';
const FileList = ({ uploadedFiles, onDelete, onView }) => {
  return (
<div className="file-list">
  {[...new Map(uploadedFiles.map(item => [item.fileName, item])).values()].map((item, index) => {
    if (item.visible) {return (
    <FileItem
      key={index}
      fileName={item.fileName}
      result={item.result}
      onDelete={() => onDelete(index)}
      onView={() => onView(item.result)}
    />);}
    else return null;
  })}
</div>
  );
};

export default FileList;
