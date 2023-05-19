import { Marked } from '@ts-stack/markdown';
import { observer } from "mobx-react";
import './App.css';
import DataStore from './datastore';

const About = observer(({ datastore }: { datastore: DataStore }) => {
    return (
        <div className="About" dangerouslySetInnerHTML={{ __html: Marked.parse("Welcome to Generative Fiction!") }} />
    );
});

export default About;
