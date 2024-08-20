import React from 'react';
import ResultItem from './ResultItem';
import '../styles/ResultList.css';
const ResultList = ({ uploadedFiles, onDelete, onView }) => {
  return (
<div className="result-list">
  {[...new Map(uploadedFiles.map(item => [item.fileName, item])).values()].map((item, index) => {
    if (item.visible) {return (
    <ResultItem
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

export default ResultList;
