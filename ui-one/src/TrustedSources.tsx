"use client";

import React from 'react';

interface TrustedSource {
  name: string;
  url: string;
  icon: string; // Optional: You can add icons if needed
  color: string; // Optional: You can add colors if needed
}

const trustedSources: TrustedSource[] = [
  { name: "NDTV", url: "https://www.ndtv.com", icon: "📰", color: "#00C9A7" },
  { name: "Indian Express", url: "https://indianexpress.com", icon: "📰", color: "#FFB800" },
  { name: "News18", url: "https://www.news18.com", icon: "📰", color: "#FF3D71" },
  { name: "Firstpost", url: "https://www.firstpost.com", icon: "📰", color: "#1E86FF" },
  { name: "Business Standard", url: "https://www.business-standard.com", icon: "📰", color: "#00C9A7" },
  { name: "DNA India", url: "https://www.dnaindia.com", icon: "📰", color: "#FFB800" },
  { name: "Deccan Chronicle", url: "https://www.deccanchronicle.com", icon: "📰", color: "#FF3D71" },
  { name: "The Quint", url: "https://www.thequint.com", icon: "📰", color: "#1E86FF" },
  { name: "Livemint", url: "https://www.livemint.com", icon: "📰", color: "#00C9A7" },
  { name: "Caravan Magazine", url: "https://www.caravanmagazine.in", icon: "📰", color: "#FFB800" },
  { name: "Alt News", url: "https://www.altnews.in", icon: "📰", color: "#FF3D71" },
  { name: "Fact Checker", url: "https://www.factchecker.in", icon: "📰", color: "#1E86FF" },
  { name: "ESPN Cricinfo", url: "https://www.espncricinfo.com", icon: "📰", color: "#00C9A7" },
  { name: "Hindustan Times", url: "https://www.hindustantimes.com", icon: "📰", color: "#FFB800" },
  { name: "Boom Live", url: "https://www.boomlive.in", icon: "📰", color: "#FF3D71" },
  { name: "Vishvas News", url: "https://www.vishvasnews.com", icon: "📰", color: "#1E86FF" },
  { name: "Factshala", url: "https://www.factshala.com", icon: "📰", color: "#00C9A7" },
  { name: "Inshorts", url: "https://www.inshorts.com", icon: "📰", color: "#FFB800" },
  { name: "Trading Economics", url: "https://www.tradingeconomics.com", icon: "📰", color: "#FF3D71" },
  { name: "Bloomberg", url: "https://www.bloomberg.com", icon: "📰", color: "#1E86FF" },
  { name: "Yahoo Finance", url: "https://www.yahoofinance.com", icon: "📰", color: "#00C9A7" },
  { name: "FT Markets", url: "https://www.ft.com/markets", icon: "📰", color: "#FFB800" },
  { name: "MarketWatch", url: "https://www.marketwatch.com", icon: "📰", color: "#FF3D71" },
  { name: "CNBC", url: "https://www.cnbc.com", icon: "📰", color: "#1E86FF" },
  { name: "Morningstar", url: "https://www.morningstar.com", icon: "📰", color: "#00C9A7" },
  { name: "Investopedia", url: "https://www.investopedia.com", icon: "📰", color: "#FFB800" },
  { name: "Oxford Research", url: "https://oxfordre.com/asianhistory", icon: "📰", color: "#FF3D71" },
  { name: "Live History India", url: "https://www.livehistoryindia.com", icon: "📰", color: "#1E86FF" },
  { name: "Gor Nation", url: "https://www.gornation.com", icon: "📰", color: "#00C9A7" },
  { name: "MyFitnessPal Blog", url: "https://blog.myfitnesspal.com", icon: "📰", color: "#FFB800" },
  { name: "Muscle & Fitness", url: "https://www.muscleandfitness.com", icon: "📰", color: "#FF3D71" },
  { name: "Runner's World", url: "https://www.runnersworld.com", icon: "📰", color: "#1E86FF" },
  { name: "CrossFit", url: "https://www.crossfit.com", icon: "📰", color: "#00C9A7" },
  { name: "Yoga Journal", url: "https://www.yogajournal.com", icon: "📰", color: "#FFB800" },
  { name: "Competitor", url: "https://www.competitor.com", icon: "📰", color: "#FF3D71" },
  { name: "T Nation", url: "https://www.tnation.com", icon: "📰", color: "#1E86FF" },
  { name: "Verywell Fit", url: "https://www.verywellfit.com", icon: "📰", color: "#00C9A7" },
  { name: "ACE Fitness", url: "https://www.acefitness.org", icon: "📰", color: "#FFB800" },
  { name: "Shape", url: "https://www.shape.com", icon: "📰", color: "#FF3D71" },
  { name: "Women's Health", url: "https://www.womenshealthmag.com", icon: "📰", color: "#1E86FF" },
  { name: "Men's Health", url: "https://www.menshealth.com", icon: "📰", color: "#00C9A7" },
  { name: "Bodybuilding", url: "https://www.bodybuilding.com", icon: "📰", color: "#FFB800" },
  { name: "Income Tax India", url: "https://www.incometaxindia.gov.in", icon: "📰", color: "#FF3D71" },
  { name: "VNR VJIET", url: "https://*.vnrvjiet.ac.in", icon: "📰", color: "#1E86FF" },
  { name: "India Government", url: "https://www.india.gov.in", icon: "📰", color: "#00C9A7" },
  { name: "DRDO", url: "https://www.drdo.gov.in", icon: "📰", color: "#FFB800" },
  { name: "Economic Times", url: "https://www.economictimes.indiatimes.com", icon: "📰", color: "#FF3D71" },
  { name: "Britannica", url: "https://www.britannica.com", icon: "📰", color: "#1E86FF" },
  { name: "Wikipedia", url: "https://en.wikipedia.org", icon: "📰", color: "#00C9A7" },
  { name: "Gadgets 360", url: "https://www.gadgets360.com", icon: "📰", color: "#FFB800" },
  { name: "Cricbuzz", url: "https://www.cricbuzz.com", icon: "📰", color: "#FF3D71" },
  { name: "Pinkvilla", url: "https://www.pinkvilla.com", icon: "📰", color: "#1E86FF" },
  { name: "Moneycontrol", url: "https://www.moneycontrol.com", icon: "📰", color: "#00C9A7" },
  { name: "Times of India", url: "https://timesofindia.indiatimes.com", icon: "📰", color: "#FFB800" },
  { name: "India Today", url: "https://www.indiatoday.in", icon: "📰", color: "#FF3D71" },
  { name: "PCMag", url: "https://www.pcmag.com", icon: "📰", color: "#1E86FF" },
  { name: "TechRadar", url: "https://www.techradar.com", icon: "📰", color: "#00C9A7" },
  { name: "The Verge", url: "https://www.theverge.com", icon: "📰", color: "#FFB800" },
  { name: "Wired", url: "https://www.wired.com", icon: "📰", color: "#FF3D71" },
  { name: "Variety", url: "https://www.variety.com", icon: "📰", color: "#1E86FF" },
  { name: "Hollywood Reporter", url: "https://www.hollywoodreporter.com", icon: "📰", color: "#00C9A7" },
  { name: "Billboard", url: "https://www.billboard.com", icon: "📰", color: "#FFB800" },
  { name: "Sky Sports", url: "https://www.skysports.com", icon: "📰", color: "#FF3D71" },
  { name: "ESPN", url: "https://www.espn.com", icon: "📰", color: "#1E86FF" },
  { name: "Business Insider", url: "https://www.businessinsider.com", icon: "📰", color: "#00C9A7" },
  { name: "Vox", url: "https://www.vox.com", icon: "📰", color: "#FFB800" },
  { name: "Forbes", url: "https://www.forbes.com", icon: "📰", color: "#FF3D71" },
  { name: "ABC News", url: "https://www.abcnews.go.com", icon: "📰", color: "#1E86FF" },
  { name: "Fox News", url: "https://www.foxnews.com", icon: "📰", color: "#00C9A7" },
  { name: "NBC News", url: "https://www.nbcnews.com", icon: "📰", color: "#FFB800" },
  { name: "Washington Post", url: "https://www.washingtonpost.com", icon: "📰", color: "#FF3D71" },
  { name: "The Guardian", url: "https://www.theguardian.com", icon: "📰", color: "#1E86FF" },
  { name: "Reuters", url: "https://www.reuters.com", icon: "📰", color: "#00C9A7" },
  { name: "BBC News", url: "https://www.bbc.com/news", icon: "📰", color: "#FFB800" },
  { name: "CNN", url: "https://www.cnn.com", icon: "📰", color: "#FF3D71" },
  { name: "New York Times", url: "https://www.nytimes.com", icon: "📰", color: "#1E86FF" },
];

interface TrustedSourcesProps {
  onClose: () => void; // Define the onClose prop type
}

export function TrustedSources() {
  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-4">
      <h2 className="text-xl font-bold">Trusted Sources</h2>
      <ul className="mt-2">
        {trustedSources.map((source, index) => (
          <li key={index} className="mb-1">
            <a href={source.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
              {source.name}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
} 