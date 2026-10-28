// Rasterize icon.svg's code-owned breathing mark with macOS system frameworks.
// Run from the project root: swift frontend/pwa/renderIcons.swift frontend/public
import Foundation
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

let output = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
func color(_ red: CGFloat, _ green: CGFloat, _ blue: CGFloat) -> CGColor {
    CGColor(red: red / 255, green: green / 255, blue: blue / 255, alpha: 1)
}
for size in [32, 192, 512] {
    let context = CGContext(data: nil, width: size, height: size, bitsPerComponent: 8,
                            bytesPerRow: 0, space: CGColorSpaceCreateDeviceRGB(),
                            bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
    context.scaleBy(x: CGFloat(size) / 512, y: CGFloat(size) / 512)
    context.translateBy(x: 0, y: 512)
    context.scaleBy(x: 1, y: -1)
    context.setFillColor(color(251, 248, 241))
    context.addPath(CGPath(roundedRect: CGRect(x: 0, y: 0, width: 512, height: 512),
                           cornerWidth: 112, cornerHeight: 112, transform: nil))
    context.fillPath()
    context.translateBy(x: 48, y: 56)
    context.scaleBy(x: 16, y: 16)
    context.setStrokeColor(color(112, 81, 142))
    context.setLineWidth(1.6)
    context.setLineCap(.round)
    context.setLineJoin(.round)
    context.move(to: CGPoint(x: 4, y: 21))
    context.addCurve(to: CGPoint(x: 18.5, y: 4), control1: CGPoint(x: 8, y: 15), control2: CGPoint(x: 13, y: 5))
    context.addCurve(to: CGPoint(x: 20.5, y: 12.5), control1: CGPoint(x: 23.5, y: 3), control2: CGPoint(x: 23.5, y: 9))
    context.addCurve(to: CGPoint(x: 13.5, y: 16), control1: CGPoint(x: 18.5, y: 15), control2: CGPoint(x: 15, y: 17))
    context.addCurve(to: CGPoint(x: 17, y: 10), control1: CGPoint(x: 11.5, y: 15), control2: CGPoint(x: 14, y: 8.5))
    context.move(to: CGPoint(x: 3, y: 14))
    context.addCurve(to: CGPoint(x: 7.5, y: 9), control1: CGPoint(x: 4, y: 12), control2: CGPoint(x: 6, y: 10))
    context.strokePath()
    let png = NSMutableData()
    let destination = CGImageDestinationCreateWithData(png, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(destination, context.makeImage()!, nil)
    precondition(CGImageDestinationFinalize(destination))
    if size == 32 {
        // One PNG-backed 32px ICO entry, for browsers requesting /favicon.ico.
        var icon = Data([0, 0, 1, 0, 1, 0, 32, 32, 0, 0, 1, 0, 32, 0])
        var length = UInt32(png.length).littleEndian
        withUnsafeBytes(of: &length) { icon.append(contentsOf: $0) }
        icon.append(contentsOf: [22, 0, 0, 0])
        icon.append(png as Data)
        try icon.write(to: output.appendingPathComponent("favicon.ico"))
    } else {
        try (png as Data).write(to: output.appendingPathComponent("icon-\(size).png"))
    }
}
