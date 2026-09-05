import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async redirects() {
    return [
      // /approach and /speaking were both hire-me pages under earlier
      // positioning. /services is the single one now, so both shapes point
      // there rather than 404ing on links already in the wild.
      {
        source: '/approach',
        destination: '/services',
        permanent: true,
      },
      {
        source: '/speaking',
        destination: '/services',
        permanent: true,
      },
      // The email archive shipped briefly as /notes. Keep both shapes alive so
      // an early link, or one already in an inbox, does not 404.
      {
        source: '/notes',
        destination: '/issues',
        permanent: true,
      },
      {
        source: '/notes/:slug',
        destination: '/issues/:slug',
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
